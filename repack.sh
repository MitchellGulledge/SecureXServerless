rm MerakiSecureXAutomation/*.log
rm *.zip
zip -r MerakiFunction.zip . -x 'venv/*' -x '.idea/*' -x '.git/*' -x 'requirements.txt'
#zip -r MerakiFunction.zip . -x 'venv/*' -x '.idea/*' -x '.git/*' -x '.python_packages/*'
git add MerakiFunction.zip
git commit -m "repack"