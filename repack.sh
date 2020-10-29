rm MerakiSecureXAutomation/*.log
rm *.zip
zip -r SecureXServerless.zip . -x 'venv/*' -x '.idea/*' -x '.git/*'
