# Decrease size gif animated
convert ../lizard.gif -coalesce temporary.gif
convert -size 146x172 temporary.gif -resize 104x123 smaller.gif
cp smaller.gif ../../gecos_gui/lizard.gif

