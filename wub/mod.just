build *_:
  just wub::slim -p supekku.slim > index.html

watch:
  xdg-open index.html
  fswatch --event Updated -0 supekku.slim styles.css | xargs -0 -n 1 just wub::build

slim *args:
  direnv exec . slimrb {{args}}

html:
  just wub::slim -p supekku.slim
