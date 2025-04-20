#!/bin/bash
# lgbtq_rag_system/scripts/setup_structure.sh

mkdir -p lgbtq_rag_system/{utils,model,fallback,logs,scripts,templates,embeddings}

# Create placeholder files
touch lgbtq_rag_system/articles.json
touch lgbtq_rag_system/logs/queries.log
touch lgbtq_rag_system/fallback/canned_response.txt
touch lgbtq_rag_system/embeddings/index.pkl

# Create sample files for utils
cat << 'EOF' > lgbtq_rag_system/utils/query.py
# (Paste the content from utils/query.py here)
EOF

cat << 'EOF' > lgbtq_rag_system/utils/retrieve.py
# (Paste the content from utils/retrieve.py here)
EOF

cat << 'EOF' > lgbtq_rag_system/utils/prompt.py
# (Paste the content from utils/prompt.py here)
EOF

# Create sample file for model
cat << 'EOF' > lgbtq_rag_system/model/llama_runner.py
# (Paste the content from model/llama_runner.py here)
EOF

# Create index.html in templates
mkdir -p lgbtq_rag_system/templates
cat << 'EOF' > lgbtq_rag_system/templates/index.html
<!-- (Paste the HTML content from templates/index.html here) -->
EOF

echo "Project structure created."
