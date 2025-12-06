function renderActionButtons(actions) {
    const container = document.createElement('div');
    container.className = 'action-buttons';

    actions
        .filter(action => action.enabled)
        .forEach(action => {
        const button = document.createElement('button');
        button.innerText = action.label;
        switch (action.id) {
            case 'game_over_restart':
                button.className = 'btn-restart';
                button.setAttribute("_", "on click restartGame()");
                break;
            default:
                button.setAttribute("_", "on click performAction('" + action.id + "')");
        }

        container.appendChild(button);
        _hyperscript.processNode(button);
    });

    document.getElementById('actions-container').replaceChildren(container);
}

function performAction(actionId) {
    console.log(`Performing action: ${actionId}`);

    const result = window.game.execute_action(actionId);
    const gameText = document.getElementById("game-text");
    gameText.innerHTML = result;
    renderActionButtons(game.available_actions());
}