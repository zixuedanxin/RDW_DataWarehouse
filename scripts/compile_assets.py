import subprocess
import os
import configparser
import shutil
import argparse


def main(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    assets_dir = config.get('default', 'assets.directory')
    smarter_dir = config.get('default', 'smarter.directory')
    run_npm = config.get('default', 'run.npm.update').lower()

    # Run cake watch - builds and watches
    try:
        current_dir = os.getcwd()
        os.chdir(assets_dir)
        if run_npm == 'true':
            # Run npm update
            command_opts = ['npm', 'update']
            rtn_code = subprocess.call(command_opts)
            if rtn_code != 0:
                print('npm install command failed')
        # Run cake to Compile
        print('Compiling coffeescripts')
        command_opts = ['node_modules/coffee-script/bin/cake', '-m', 'PROD', '-a', assets_dir, '-s', smarter_dir, 'setup']
        rtn_code = subprocess.call(command_opts)
        if rtn_code != 0:
            print('cake command failed in compiling')
        # Optimize javascript
        print('Optimize javascript')
        command_opts = ['node_modules/coffee-script/bin/cake', '-m', 'PROD', '-a', assets_dir, '-s', smarter_dir, 'optimize']
        rtn_code = subprocess.call(command_opts)
        if rtn_code != 0:
            print('cake command failed in optimizing javascript')
        # Copy Assets
        print('Copying Assets')
        command_opts = ['node_modules/coffee-script/bin/cake', '-m', 'PROD', '-a', assets_dir, '-s', smarter_dir, 'copy']
        rtn_code = subprocess.call(command_opts)
        if rtn_code != 0:
            print('cake command failed in copying')
    except Exception as ex:
        print("Exception occurred " + str(ex))
    finally:
        # Change the directory back to original
        os.chdir(current_dir)

if __name__ == '__main__':
    this_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(this_file)

    parser = argparse.ArgumentParser(description='Compile Assets and Copy Asssets into Smarter')
    parser.add_argument('--config', default=os.path.join(current_dir, 'compile_assets.ini'), help='Set the path to configuration ini file (defaults to compile_assets.ini')
    args = parser.parse_args()

    main(args.config)
