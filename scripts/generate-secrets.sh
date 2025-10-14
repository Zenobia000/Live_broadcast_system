#!/bin/bash
# Generate secure secrets for the Smart Attendance System

set -e

SECRETS_DIR="$(dirname "$0")/../infrastructure/docker/secrets"
mkdir -p "$SECRETS_DIR"

echo "🔐 Generating secure secrets for Smart Attendance System..."

# Generate JWT Secret (256-bit)
if [ ! -f "$SECRETS_DIR/jwt_secret.txt" ]; then
    echo "Generating JWT secret..."
    python3 -c "import secrets; print(secrets.token_urlsafe(32))" > "$SECRETS_DIR/jwt_secret.txt"
    echo "✅ JWT secret generated"
fi

# Generate Database Password
if [ ! -f "$SECRETS_DIR/db_password.txt" ]; then
    echo "Generating database password..."
    python3 -c "import secrets; import string; print(''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*()') for _ in range(24)))" > "$SECRETS_DIR/db_password.txt"
    echo "✅ Database password generated"
fi

# Create database user file
if [ ! -f "$SECRETS_DIR/db_user.txt" ]; then
    echo "attendance_user" > "$SECRETS_DIR/db_user.txt"
    echo "✅ Database user file created"
fi

# Create database name file
if [ ! -f "$SECRETS_DIR/db_name.txt" ]; then
    echo "attendance_db" > "$SECRETS_DIR/db_name.txt"
    echo "✅ Database name file created"
fi

# Create placeholder for Google client secret
if [ ! -f "$SECRETS_DIR/google_client_secret.txt" ]; then
    echo "YOUR_GOOGLE_CLIENT_SECRET_HERE" > "$SECRETS_DIR/google_client_secret.txt"
    echo "⚠️  Google client secret placeholder created - REPLACE WITH ACTUAL SECRET"
fi

# Set secure permissions
chmod 600 "$SECRETS_DIR"/*.txt
echo "🔒 Set secure permissions on all secret files"

echo ""
echo "📋 Next steps:"
echo "1. Edit $SECRETS_DIR/google_client_secret.txt with your actual Google OAuth secret"
echo "2. Review and update other secrets as needed"
echo "3. Never commit these files to git"
echo ""
echo "🔐 Secret generation completed successfully!"

# Create .env file from template if it doesn't exist
ENV_FILE="$(dirname "$0")/../src/backend/.env"
ENV_EXAMPLE="$(dirname "$0")/../src/backend/.env.example"

if [ ! -f "$ENV_FILE" ] && [ -f "$ENV_EXAMPLE" ]; then
    echo ""
    echo "📝 Creating .env file from template..."
    cp "$ENV_EXAMPLE" "$ENV_FILE"

    # Replace placeholders with generated secrets
    JWT_SECRET=$(cat "$SECRETS_DIR/jwt_secret.txt")
    DB_PASSWORD=$(cat "$SECRETS_DIR/db_password.txt")

    # Replace in .env file (MacOS/Linux compatible)
    sed -i.bak "s/<GENERATE_256_BIT_SECRET>/$JWT_SECRET/g" "$ENV_FILE" && rm "$ENV_FILE.bak"
    sed -i.bak "s/<GENERATE_STRONG_PASSWORD>/$DB_PASSWORD/g" "$ENV_FILE" && rm "$ENV_FILE.bak"

    echo "✅ .env file created with generated secrets"
    echo "⚠️  Please edit .env to add your Google OAuth credentials"
fi