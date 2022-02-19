__all__ = [
    'bulk_rename_files',
    'rename_file'
]

import logging
import re
import shutil
import sys

from pathlib import Path

# Initialize logger
LOG_FMT_STRING = (
    '[%(asctime)]s %(levelname)s %(module)s %(lineno)d - %(message)s'
)

logging.basicConfig(level=logging.INFO, format=LOG_FMT_STRING)
log = logging.getLogger(__name__)

def get_files(target_path, filter_pat=None):
    try:
        if filter_pat:
            filter_pat = re.compile(filter_pat)
            log.debug(f'Searching files matching pattern: {filter_pat.pattern}')
    except Exception as err:
        msg = f'Invalid filter: {err}'
        log.error(msg)
        raise Exception(msg)
        
    for file_ in target_path.iterdir():
        if filter_pat:
            if filter_pat.match(file_.name):
                yield file_
            else:
                log.debug(f'File {file_.name} did not match pattern.')
        else:
            yield file_
            
def rename_file(file_path, new_name, counter=None):
    counter = counter or ''
    new_name = f'{new_name}{counter}{file_path.suffix}'
    new_path = file_path.parent.joinpath(new_name)
    shutil.move(file_path, new_path)
    log.info(f'Renamed {file_path.name} -> {new_path.name}')
    return new_path
    
def bulk_rename_files(target_dir, new_name, file_pattern=None):
    target_dir = Path(target_dir)
    if not target_dir.is_dir():
        log.error('f{target_dir} does not exist or is not a directory.')
        return False
        
    counter = 1
    for file_ in get_files(target_dir, filter_pat=file_pattern):
        log.debug(f'Found {file_}')
        rename_file(file_, new_name, counter=counter)
        counter += 1
    return True
    
def main(args):
    try:
        success = bulk_rename_files(args.target_dir, args.new_name, args.file_pattern)
        if success:
            log.info('Done.')
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception:
        sys.exit(1)
        
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        'new_name',
        help=('Files matching `file_pattern` will be renamed with this value.'
            'An incrementing count will also be added.'))
        
    parser.add_argument(
        'file_pattern',
        help='Files to rename (Regex compatible).')
        
    parser.add_argument(
        'target_dir',
        help='Directory where the files to rename reside.')
        
    parser.add_argument(
        '-L', '--log-level',
        help='Set log level.',
        default='info')
        
    args = parser.parse_args()
    
    # Configure logger
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format=LOG_FMT_STRING,
    )
    
    main(args)      

