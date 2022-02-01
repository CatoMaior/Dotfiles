#!/bin/bash
mkdir -p /usr/share/i3blocks
mv -r Config/i3blocks/i3blocksScripts /usr/share/i3blocks
mkdir -p /usr/share/rofi/themes
mv Config/rofi/transparent.rasi /usr/share/rofi/themes/
mkdir -p $HOME/Scripts
mkdir -p $HOME/.config
cp Scripts $HOME/Scripts
cp Config/* $HOME/.config
