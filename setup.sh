echo '#!/bin/bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
[theme]\n\
backgroundColor = \"#FFFFFF\"\n\
" > ~/.streamlit/config.toml' > setup.sh