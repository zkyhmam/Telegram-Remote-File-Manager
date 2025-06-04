# -*- coding: utf-8 -*-
"""
Core logic for performing file and directory searches.
"""
import os
import re
import logging
from pathlib import Path
from stat import S_ISLNK
from typing import List, Dict, Any, Optional, Tuple

from config import START_DIRECTORY_PATH, SEARCH_RESULTS_LIMIT
import localization as loc
from .helpers import escape_html

logger = logging.getLogger(__name__)

def perform_search(
    search_term_raw: str,
    search_path: Path
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Performs a recursive search for files and directories.

    Args:
        search_term_raw: The raw search term from the user.
        search_path: The Path object for the directory to search within.

    Returns:
        A tuple containing:
        - A list of result dictionaries.
        - An optional error message string.
    """
    results: List[Dict[str, Any]] = []
    search_error: Optional[str] = None
    processed_inodes = set() # To handle symlink loops or duplicate entries via symlinks

    try:
        # Prepare regex pattern from search term
        # Escape user input for regex, then replace user's '*' with '.*'
        safe_term_for_regex = re.escape(search_term_raw).replace('\\*', '.*')
        pattern = re.compile(safe_term_for_regex, re.IGNORECASE)
        logger.debug(f"Search regex pattern: '{pattern.pattern}' for term '{search_term_raw}' in '{search_path}'")

        for root, dirs, files in os.walk(search_path, topdown=True, onerror=None, followlinks=False):
            current_root_path = Path(root)

            # Security check: Ensure we are still within START_DIRECTORY_PATH
            if not (current_root_path.resolve() == START_DIRECTORY_PATH or \
                    str(current_root_path.resolve()).startswith(str(START_DIRECTORY_PATH) + os.sep)):
                logger.warning(f"Search ventured outside allowed root: {current_root_path}. Pruning.")
                dirs[:] = []  # Don't recurse further into these directories
                continue

            # Process directories
            # Iterate over a copy of dirs for safe modification
            dirs_to_remove = []
            for dirname in list(dirs):
                if len(results) >= SEARCH_RESULTS_LIMIT: break
                dirpath = current_root_path / dirname
                try:
                    dir_stat = dirpath.lstat() # Use lstat to get info about the link itself
                    is_symlink = S_ISLNK(dir_stat.st_mode)
                    
                    # Skip if symlink loop detected or already processed this inode via another link
                    if is_symlink and dir_stat.st_ino in processed_inodes:
                        dirs_to_remove.append(dirname)
                        continue
                    processed_inodes.add(dir_stat.st_ino)

                    if pattern.search(dirname):
                        resolved_dir_path_str = str(dirpath.resolve()) # Resolve for consistency
                        is_target_dir = False
                        # Check if resolved path is within bounds and is a directory
                        try:
                            resolved_path = dirpath.resolve(strict=True) # strict to catch broken links early
                            if (resolved_path == START_DIRECTORY_PATH or \
                                str(resolved_path).startswith(str(START_DIRECTORY_PATH) + os.sep)):
                                is_target_dir = resolved_path.is_dir()
                                resolved_dir_path_str = str(resolved_path)
                            else: # Symlink points out of bounds
                                resolved_dir_path_str = str(dirpath) # Use link path, mark as non-dir
                                is_target_dir = False
                        except (OSError, FileNotFoundError): # Broken symlink or permission issue
                            resolved_dir_path_str = str(dirpath) # Use link path
                            is_target_dir = False


                        results.append({
                            "name": dirname,
                            "path": resolved_dir_path_str,
                            "is_dir": is_target_dir,
                            "is_file": False,
                            "is_symlink": is_symlink
                        })
                except OSError as e:
                    logger.warning(f"OSError checking directory {escape_html(str(dirpath))}: {e}. Pruning from search.")
                    dirs_to_remove.append(dirname)
                except Exception as e: # Catch any other errors during dir processing
                    logger.warning(f"Unexpected error with directory {escape_html(str(dirpath))}: {e}. Pruning.")
                    dirs_to_remove.append(dirname)
            
            # Prune dirs marked for removal
            for d_rem in dirs_to_remove:
                if d_rem in dirs: dirs.remove(d_rem)

            if len(results) >= SEARCH_RESULTS_LIMIT: break

            # Process files
            for filename in files:
                if len(results) >= SEARCH_RESULTS_LIMIT: break
                filepath = current_root_path / filename
                try:
                    if pattern.search(filename):
                        file_stat = filepath.lstat() # Info about link itself
                        is_symlink = S_ISLNK(file_stat.st_mode)
                        
                        resolved_file_path_str = str(filepath.resolve())
                        is_target_file = False

                        try:
                            resolved_path = filepath.resolve(strict=True)
                            if (resolved_path == START_DIRECTORY_PATH or \
                                str(resolved_path).startswith(str(START_DIRECTORY_PATH) + os.sep)):
                                is_target_file = resolved_path.is_file()
                                resolved_file_path_str = str(resolved_path)
                            else: # Symlink points out of bounds
                                resolved_file_path_str = str(filepath)
                                is_target_file = False
                        except (OSError, FileNotFoundError): # Broken symlink
                             resolved_file_path_str = str(filepath)
                             is_target_file = False
                        
                        results.append({
                            "name": filename,
                            "path": resolved_file_path_str,
                            "is_dir": False,
                            "is_file": is_target_file,
                            "is_symlink": is_symlink
                        })
                except OSError as e:
                    logger.warning(f"OSError checking file {escape_html(str(filepath))}: {e}. Skipping.")
                except Exception as e:
                    logger.warning(f"Unexpected error with file {escape_html(str(filepath))}: {e}. Skipping.")
            if len(results) >= SEARCH_RESULTS_LIMIT: break
        
        # Sort results: directories first, then by name
        results.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))


    except PermissionError as e:
        search_error = loc.SEARCH_ERROR_PERMISSION
        logger.error(f"Permission denied starting os.walk at {search_path}: {e}")
    except Exception as e:
        search_error = loc.SEARCH_ERROR_GENERAL.format(error=escape_html(str(e)))
        logger.exception(f"Error during search in {search_path} for '{search_term_raw}': {e}")

    return results[:SEARCH_RESULTS_LIMIT], search_error

# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
