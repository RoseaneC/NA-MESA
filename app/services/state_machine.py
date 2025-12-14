from __future__ import annotations

from typing import Dict, List, Tuple

from .local_support import get_local_support

GREETING = "Oi! Eu sou a VEXIA 🤍 Posso te ajudar agora. Escolha uma opção:"


def normalize(message: str) -> str:
    return (message or "").strip().lower()


def includes_any(message: str, keywords: List[str]) -> bool:
    text = normalize(message)
    return any(k in text for k in keywords)


def menu_response(context: Dict) -> Tuple[str, List[str], str, Dict]:
    quick = ["Quero doar", "Sou uma ONG", "Preciso de comida", "Quero voluntariar"]
    return GREETING, quick, "MENU", context


def handle_global_commands(message: str):
    text = normalize(message)
    if text == "menu":
        return "Voltando ao menu inicial.", [], "MENU", {}
    if text == "reiniciar":
        return "Sessão reiniciada. Vamos começar de novo!", [], "MENU", {}
    if text == "ajuda":
        reply = (
            "Posso ajudar com doações, cadastro de ONG, pedidos de comida "
            "ou voluntariado. Escolha uma opção ou digite Menu para voltar."
        )
        return reply, ["Quero doar", "Sou uma ONG", "Preciso de comida", "Quero voluntariar"], None, None
    return None


def handle_message(state: str, context: Dict, message: str):
    state = state or "MENU"
    context = context or {}
    message = message or ""

    # Comandos globais
    global_cmd = handle_global_commands(message)
    if global_cmd:
        reply, quick, new_state, new_ctx = global_cmd
        if new_state is None:  # apenas ajuda
            return reply, quick, state, context
        return reply, quick or ["Menu"], new_state, new_ctx

    # Se vazio, mostra menu
    if not message.strip():
        return menu_response(context)

    text = normalize(message)

    # MENU
    if state == "MENU":
        if includes_any(text, ["doar", "doação", "doacao"]):
            context = {"fluxo": "Doação"}
            return "Legal! Em qual bairro você está?", [], "DOAR_BAIRRO", context
        if includes_any(text, ["ong"]):
            context = {"fluxo": "ONG"}
            return "Vamos cadastrar sua ONG. Qual o nome?", [], "ONG_NOME", context
        if includes_any(text, ["preciso", "comida", "fome"]):
            context = {"fluxo": "Pedido"}
            return "Vamos ajudar! Qual seu bairro?", [], "SEEKER_BAIRRO", context
        if includes_any(text, ["volunt", "ajudar"]):
            context = {"fluxo": "Voluntariado"}
            return "Demais! Em qual bairro você pode atuar?", [], "VOL_BAIRRO", context
        # não reconhecido
        reply, quick, _, _ = menu_response(context)
        return f"Não entendi, mas posso ajudar. {reply}", quick, "MENU", context

    # DOAR fluxos
    if state == "DOAR_BAIRRO":
        context["bairro"] = message.strip()
        return "Que tipo de doação você quer enviar?", ["Marmitas", "Cesta básica", "Alimentos avulsos"], "DOAR_TIPO", context

    if state == "DOAR_TIPO":
        options = {"marmitas": "Marmitas", "cesta básica": "Cesta básica", "cesta basica": "Cesta básica", "alimentos": "Alimentos avulsos", "alimentos avulsos": "Alimentos avulsos"}
        for key, label in options.items():
            if key in text:
                context["tipo"] = label
                return "Quantas unidades você pode doar?", [], "DOAR_QTD", context
        return "Pode escolher uma opção?", list(options.values()), state, context

    if state == "DOAR_QTD":
        context["quantidade"] = message.strip()
        return "Quando consegue entregar?", ["Agora", "Hoje", "Amanhã", "Essa semana"], "DOAR_HORARIO", context

    if state == "DOAR_HORARIO":
        choices = ["agora", "hoje", "amanhã", "amanha", "essa semana", "semana"]
        if any(c in text for c in choices):
            context["horario"] = message.strip().capitalize()
            resumo = (
                f"Doação: {context.get('tipo','?')}\n"
                f"Bairro: {context.get('bairro','?')}\n"
                f"Quantidade: {context.get('quantidade','?')}\n"
                f"Quando: {context.get('horario','?')}"
            )
            reply = "Perfeito! Confere o resumo:\n" + resumo
            return reply, ["Confirmar", "Editar", "Menu"], "DOAR_CONFIRM", context
        return "Escolha uma opção de horário:", ["Agora", "Hoje", "Amanhã", "Essa semana"], state, context

    if state == "DOAR_CONFIRM":
        if "confirm" in text:
            reply = (
                "Registrado ✅ Em uma versão completa, a VEXIA faz o match "
                "com ONGs/voluntários próximos e confirma a retirada/entrega."
            )
            return reply, ["Menu"], "DOAR_DONE", context
        if "editar" in text:
            return "Vamos ajustar. Qual o bairro?", [], "DOAR_BAIRRO", context
        if "menu" in text:
            return "Voltando ao menu.", ["Quero doar", "Sou uma ONG", "Preciso de comida", "Quero voluntariar"], "MENU", context
        return "Pode escolher Confirmar, Editar ou Menu?", ["Confirmar", "Editar", "Menu"], state, context

    if state == "DOAR_DONE":
        return menu_response(context)

    # ONG fluxos
    if state == "ONG_NOME":
        context["ong_nome"] = message.strip()
        return "Qual bairro vocês atendem?", [], "ONG_BAIRRO", context

    if state == "ONG_BAIRRO":
        context["bairro"] = message.strip()
        return "Como estão as necessidades?", ["Recebo doações", "Preciso de doações", "Ambos"], "ONG_NECESSIDADE", context

    if state == "ONG_NECESSIDADE":
        opts = ["recebo doações", "preciso de doações", "ambos", "recebo", "preciso"]
        if any(o in text for o in opts):
            context["necessidade"] = message.strip().capitalize()
            resumo = (
                f"ONG: {context.get('ong_nome','?')}\n"
                f"Bairro: {context.get('bairro','?')}\n"
                f"Necessidade: {context.get('necessidade','?')}"
            )
            reply = "Tudo certo. Confirma esse cadastro?\n" + resumo
            return reply, ["Confirmar", "Editar", "Menu"], "ONG_CONFIRM", context
        return "Escolha uma opção:", ["Recebo doações", "Preciso de doações", "Ambos"], state, context

    if state == "ONG_CONFIRM":
        if "confirm" in text:
            reply = (
                "Registrado ✅ Em uma versão completa, a VEXIA faz o match "
                "com ONGs/voluntários próximos e confirma a retirada/entrega."
            )
            return reply, ["Menu"], "ONG_DONE", context
        if "editar" in text:
            return "Vamos ajustar. Qual o nome da ONG?", [], "ONG_NOME", context
        if "menu" in text:
            return "Voltando ao menu.", ["Quero doar", "Sou uma ONG", "Preciso de comida", "Quero voluntariar"], "MENU", context
        return "Pode escolher Confirmar, Editar ou Menu?", ["Confirmar", "Editar", "Menu"], state, context

    if state == "ONG_DONE":
        return menu_response(context)

    # SEEKER fluxos
    if state == "SEEKER_BAIRRO":
        context["bairro"] = message.strip()
        return "Quantas pessoas precisam de comida?", [], "SEEKER_PESSOAS", context

    if state == "SEEKER_PESSOAS":
        context["pessoas"] = message.strip()
        return "Qual a urgência?", ["Hoje", "Amanhã", "Essa semana"], "SEEKER_URGENCIA", context

    if state == "SEEKER_URGENCIA":
        opts = ["hoje", "amanhã", "amanha", "essa semana", "semana"]
        if any(o in text for o in opts):
            context["urgencia"] = message.strip().capitalize()
            resumo = (
                f"Bairro: {context.get('bairro','?')}\n"
                f"Pessoas: {context.get('pessoas','?')}\n"
                f"Urgência: {context.get('urgencia','?')}"
            )
            reply = "Entendido. Confirma o pedido?\n" + resumo
            return reply, ["Confirmar", "Editar", "Menu"], "SEEKER_CONFIRM", context
        return "Escolha uma opção de urgência:", ["Hoje", "Amanhã", "Essa semana"], state, context

    if state == "SEEKER_CONFIRM":
        if "confirm" in text:
            supports = get_local_support(context.get("bairro", ""))
            if supports:
                lines = []
                for s in supports:
                    titulo = (
                        f"🍲 {s['nome']} — {s.get('distance_km', '?')} km"
                        if s["tipo"] == "cozinha_solidaria"
                        else f"📦 {s['nome']} — {s.get('distance_km', '?')} km"
                    )
                    linhas = [
                        titulo,
                        f"📍 {s['endereco']}",
                        f"🕒 {s.get('days','')} • {s['horario']}",
                    ]
                    lines.append("\n".join(linhas))
                support_msg = "Encontrei apoios próximos:\n\n" + "\n\n".join(lines)
                quick = ["Ver detalhes", "Novo pedido", "Menu"]
            else:
                support_msg = (
                    "Ainda não temos parceiros cadastrados nesse bairro. "
                    "Em uma versão completa, a VEXIA conecta isso em tempo real com ONGs ativas."
                )
                quick = ["Novo pedido", "Menu"]

            reply = (
                "Registrado ✅ Em uma versão completa, a VEXIA faz o match "
                "com ONGs/voluntários próximos e confirma a retirada/entrega.\n\n"
                + support_msg
            )
            return reply, quick, "SEEKER_DONE", context
        if "editar" in text:
            return "Vamos ajustar. Qual o bairro?", [], "SEEKER_BAIRRO", context
        if "menu" in text:
            return "Voltando ao menu.", ["Quero doar", "Sou uma ONG", "Preciso de comida", "Quero voluntariar"], "MENU", context
        return "Pode escolher Confirmar, Editar ou Menu?", ["Confirmar", "Editar", "Menu"], state, context

    if state == "SEEKER_DONE":
        supports = get_local_support(context.get("bairro", ""))
        if includes_any(text, ["ver detalhes"]) and supports:
            detail_lines = []
            for s in supports:
                titulo = (
                    f"🍲 {s['nome']} — {s.get('distance_km','?')} km"
                    if s["tipo"] == "cozinha_solidaria"
                    else f"📦 {s['nome']} — {s.get('distance_km','?')} km"
                )
                phone = f"📞 {s['phone']}" if s.get("phone") else ""
                linhas = [
                    titulo,
                    f"📍 {s['endereco']}",
                    f"🕒 {s.get('days','')} • {s['horario']}",
                ]
                if phone:
                    linhas.append(phone)
                detail_lines.append("\n".join(linhas))
            reply = "Detalhes dos apoios:\n\n" + "\n\n".join(detail_lines)
            return reply, ["Abrir no Admin", "Menu"], "SEEKER_DETAILS", context

        if supports:
            lines = []
            for s in supports:
                titulo = (
                    f"🍲 {s['nome']} — {s.get('distance_km', '?')} km"
                    if s["tipo"] == "cozinha_solidaria"
                    else f"📦 {s['nome']} — {s.get('distance_km', '?')} km"
                )
                linhas = [
                    titulo,
                    f"📍 {s['endereco']}",
                    f"🕒 {s.get('days','')} • {s['horario']}",
                ]
                lines.append("\n".join(linhas))
            support_msg = "Encontrei apoios próximos:\n\n" + "\n\n".join(lines)
            quick = ["Ver detalhes", "Novo pedido", "Menu"]
        else:
            support_msg = (
                "Ainda não temos parceiros cadastrados nesse bairro. "
                "Em uma versão completa, a VEXIA conecta isso em tempo real com ONGs ativas."
            )
            quick = ["Novo pedido", "Menu"]

        reply = (
            "Registrado ✅ Em uma versão completa, a VEXIA faz o match "
            "com ONGs/voluntários próximos e confirma a retirada/entrega.\n\n"
            + support_msg
        )
        return reply, quick, "SEEKER_DONE", context

    if state == "SEEKER_DETAILS":
        if includes_any(text, ["abrir no admin"]):
            reply = "Acesse /admin para ver as sessões."
            return reply, ["Menu"], "MENU", context
        if includes_any(text, ["menu"]):
            return "Voltando ao menu.", ["Quero doar", "Sou uma ONG", "Preciso de comida", "Quero voluntariar"], "MENU", context
        return "Você pode escolher 'Abrir no Admin' ou 'Menu'.", ["Abrir no Admin", "Menu"], state, context

    # VOLUNTARIO fluxos
    if state == "VOL_BAIRRO":
        context["bairro"] = message.strip()
        return "Qual período você pode ajudar?", ["Manhã", "Tarde", "Noite", "Fim de semana"], "VOL_DISPON", context

    if state == "VOL_DISPON":
        opts = ["manhã", "manha", "tarde", "noite", "fim de semana", "semana"]
        if any(o in text for o in opts):
            context["disponibilidade"] = message.strip().capitalize()
            return "Pode compartilhar um telefone ou Instagram para contato?", [], "VOL_CONTATO", context
        return "Escolha um período:", ["Manhã", "Tarde", "Noite", "Fim de semana"], state, context

    if state == "VOL_CONTATO":
        context["contato"] = message.strip()
        resumo = (
            f"Bairro: {context.get('bairro','?')}\n"
            f"Disponibilidade: {context.get('disponibilidade','?')}\n"
            f"Contato: {context.get('contato','?')}"
        )
        reply = "Obrigada! Confirma seu cadastro de voluntário?\n" + resumo
        return reply, ["Confirmar", "Editar", "Menu"], "VOL_CONFIRM", context

    if state == "VOL_CONFIRM":
        if "confirm" in text:
            reply = (
                "Registrado ✅ Em uma versão completa, a VEXIA faz o match "
                "com ONGs/voluntários próximos e confirma a retirada/entrega."
            )
            return reply, ["Menu"], "VOL_DONE", context
        if "editar" in text:
            return "Vamos ajustar. Qual o bairro?", [], "VOL_BAIRRO", context
        if "menu" in text:
            return "Voltando ao menu.", ["Quero doar", "Sou uma ONG", "Preciso de comida", "Quero voluntariar"], "MENU", context
        return "Pode escolher Confirmar, Editar ou Menu?", ["Confirmar", "Editar", "Menu"], state, context

    if state == "VOL_DONE":
        return menu_response(context)

    # fallback
    reply, quick, _, _ = menu_response(context)
    return f"Não entendi, vamos começar de novo. {reply}", quick, "MENU", {}

