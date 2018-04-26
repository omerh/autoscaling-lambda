
PROJECT = autoscaling-lambda
VIRTUAL_ENV = venv
FUNCTION_NAME = autoscaling-lambda
AWS_REGION = [enter your region]
FUNCTION_HANDLER = lambda_handler
LAMBDA_ROLE = [enter your ARN lambda]

# Default commands
install: virtual install_libs
build: clean_package build_package_tmp install_libs copy_python remove_unused zip
deploy: lambda_update
full: clean_package build_package_tmp install_libs copy_python remove_unused zip git_update lambda_update

virtual:
	@echo
		if test ! -d "$(VIRTUAL_ENV)"; then \
			pip install virtualenv; \
			virtualenv $(VIRTUAL_ENV); \
		fi
	@echo

source_env:
	source ./env/bin/activate

install_libs:
	pip install boto3

clean_package:
	rm -rf ./package/*

build_package_tmp:
	mkdir -p ./package/tmp/lib
	cp -a ./$(PROJECT)/. ./package/tmp

copy_python:
	if test -d $(VIRTUAL_ENV)/lib; then \
		cp -a $(VIRTUAL_ENV)/lib/python3.6/site-packages/. ./package/tmp/; \
	fi
	if test -d $(VIRTUAL_ENV)/lib64; then \
		cp -a $(VIRTUAL_ENV)/lib64/python3.6/site-packages/. ./package/tmp/; \
	fi

remove_unused:
	rm -rf ./package/tmp/wheel*
	rm -rf ./package/tmp/easy-install*
	rm -rf ./package/tmp/setuptools*

zip:
	cd ./package/tmp && zip -r ../../$(PROJECT).zip .

git_update:
	git add .
	git commit -m 'new code before deploy to aws lambda'
	git push origin master

lambda_delete:
	aws lambda delete-function \
		--function_name $(FUNCTION_NAME)

lambda_update:
	aws lambda update-function-code \
		--region $(AWS_REGION) \
		--function-name $(FUNCTION_NAME) \
		--zip-file fileb://$(PROJECT).zip \
		--publish

lambda_update_dry:
	aws lambda update-function-code \
		--region $(AWS_REGION) \
		--function-name $(FUNCTION_NAME) \
		--zip-file fileb://$(PROJECT).zip \
		--dry-run

lambda_create:
	aws lambda create-function \
		--region $(AWS_REGION) \
		--function-name $(FUNCTION_NAME) \
		--zip-file fileb://$(PROJECT).zip \
		--role $(LAMBDA_ROLE) \
		--handler $(PROJECT).$(FUNCTION_HANDLER) \
		--runtime python3.6 \
		--timeout 30 \
		--memory-size 64