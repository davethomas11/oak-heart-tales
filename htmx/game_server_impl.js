game_server.onGet("/game", () => {
    window.game = newGame();
    return `<pre id="game-text">${window.game.look()}</pre>
            <div id="actions-container">${getActionsHtml()}</div>`;
});

game_server.onGet("/actions", () => {
    return getActionsHtml();
});

game_server.onGet(/.*\/execute\?.*/, (request, params) => {
    const actionId = params['action_id'];
    try {
        const result = window.game.execute_action(actionId);
        return `<pre id="game-text">${result}</pre>`
    } catch (e) {
        console.error(e);
        return `<pre id="game-text">${e}</pre>`
    }
});

function getActionHypertext(actionId) {
    const processActions = `then fetch '/actions'
                    then put the result into #actions-container.innerHTML
                    then _hyperscript.processNode(#actions-container)`;
    switch (actionId) {
        case 'game_over_restart':
            return "on click restartGame() " + processActions;
        default:
            return `on click fetch '/execute?action_id=${actionId}' 
                    then put the result into #game-text.innerHTML
                    ${processActions}
                    `;
    }
}

function getActionsHtml() {
    const actions = window.game.available_actions();
    return actions
        .filter(action => action.enabled)
        .map(action => `
            <button _="${getActionHypertext(action.id)}">
            ${action.label}
            </button>`)
        .join('');
}