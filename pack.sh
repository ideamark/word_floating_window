rm -rf build dist *.spec
sleep 1
pyinstaller --onefile --windowed --name "单词浮窗" --icon "favicon.ico" --add-binary "stardict.db:." main.py

mkdir -p dist/dmg
cp -r "dist/单词浮窗.app" dist/dmg
create-dmg \
  --volname "单词浮窗" \
  --volicon "favicon.ico" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "单词浮窗.app" 175 120 \
  --hide-extension "单词浮窗.app" \
  --app-drop-link 425 120 \
  "dist/单词浮窗.dmg" \
  "dist/dmg/"