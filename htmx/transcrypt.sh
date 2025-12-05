transcrypt -b -n -od js ../engine/game/game.py

mkdir -p js
cp ../engine/game/__target__/*.js js/
