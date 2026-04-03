#!/bin/bash
# Hook: PreToolUse - Block dangerous actions
# Based on FlorianBruniaux/claude-code-ultimate-guide (CC BY-SA 4.0)
# Modified: removed token= pattern, fixed done->fi bug, added attribution
# Exit 0 = allow, Exit 2 = block

set -e

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input // empty')

# === BASH: Dangerous commands ===
if [[ "$TOOL_NAME" == "Bash" ]]; then
    COMMAND=$(echo "$TOOL_INPUT" | jq -r '.command // empty')

    DANGEROUS_PATTERNS=(
        "rm -rf /"
        "rm -rf ~"
        "rm -rf \$HOME"
        "dd if="
        "mkfs"
        ":(){:|:&};:"
        "> /dev/sda"
        "chmod -R 777 /"
        "chown -R"
        "sudo rm"
        "DROP DATABASE"
        "DROP TABLE"
        "--no-preserve-root"
    )

    for pattern in "${DANGEROUS_PATTERNS[@]}"; do
        if [[ "$COMMAND" == *"$pattern"* ]]; then
            echo "BLOCKED: Dangerous command detected: '$pattern'" >&2
            exit 2
        fi
    done

    if echo "$COMMAND" | grep -qE "git push.*(-f|--force).*(main|master)"; then
        echo "BLOCKED: Force push to main/master is forbidden" >&2
        exit 2
    fi

    if echo "$COMMAND" | grep -qE "npm publish|pnpm publish|yarn publish"; then
        echo "BLOCKED: Package publication requires manual confirmation" >&2
        exit 2
    fi

    SECRET_PATTERNS=(
        "password="
        "secret="
        "api_key="
        "apikey="
        "aws_access_key"
        "aws_secret"
        "private_key"
    )

    for pattern in "${SECRET_PATTERNS[@]}"; do
        if echo "$COMMAND" | grep -qi "$pattern"; then
            echo "BLOCKED: Potential secret detected in command: '$pattern'" >&2
            exit 2
        fi
    done
fi

# === EDIT/WRITE: Sensitive files ===
if [[ "$TOOL_NAME" == "Edit" || "$TOOL_NAME" == "Write" ]]; then
    FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path // empty')

    PROTECTED_FILES=(
        ".env"
        ".env.local"
        ".env.production"
        ".env.development"
        "credentials.json"
        "serviceAccountKey.json"
        "id_rsa"
        "id_ed25519"
        "id_ecdsa"
        ".npmrc"
        ".pypirc"
        "secrets.yml"
        "secrets.yaml"
    )

    FILENAME=$(basename "$FILE_PATH")
    for protected in "${PROTECTED_FILES[@]}"; do
        if [[ "$FILENAME" == "$protected" ]]; then
            echo "BLOCKED: Editing sensitive file '$FILENAME' is forbidden" >&2
            exit 2
        fi
    done
fi

# === DELETE: Always warn ===
if [[ "$TOOL_NAME" == "Bash" ]]; then
    COMMAND=$(echo "$TOOL_INPUT" | jq -r '.command // empty')
    if echo "$COMMAND" | grep -qE "rm -r|rmdir|unlink"; then
        echo '{"systemMessage": "Warning: File deletion detected. Verify this is intentional."}'
    fi
fi

exit 0
