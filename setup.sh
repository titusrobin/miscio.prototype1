#!/bin/bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = $PORT\n\
\n\
[theme]\n\
backgroundColor = \"#FFFFFF\"\n\
" > ~/.streamlit/config.toml