rm MerakiSecureXAutomation/*.log
rm *.zip
zip -r MerakiFunction.zip . -x 'venv/*' -x '.idea/*' -x '.git/*'
