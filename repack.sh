rm *.zip
rm -rf .python_packages
pip install --target=./.python_packages/lib/site-packages -r requirements.txt
zip -r MerakiFunction.zip . -x 'venv/*' -x '.idea/*' -x '.git/*' -x 'requirements.txt'
#zip -r MerakiFunction.zip . -x 'venv/*' -x '.idea/*' -x '.git/*' -x '.python_packages/*'
git add MerakiFunction.zip
git commit -m "repack"
