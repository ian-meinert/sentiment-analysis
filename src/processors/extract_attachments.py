"""
This script processes email messages in .msg format from a specified input directory,
extracts .docx attachments from emails sent by specified senders, and saves the attachments
to a specified output directory.
Functions:
    _init_data_paths(out_folder, in_folder=None):
        Initializes the data paths by creating the output folder if it doesn't exist
        and ensuring the input folder exists if provided
    find_and_save_attachments(msg: Message, save_path):
        Finds and saves .docx attachments from an email message to a specified directory
    parse_from_path(senders: list = None, path_in=DEFAULT_PATH_IN, path_out=DEFAULT_PATH_OUT):
        Parses email messages from a specified input directory and processes them
        based on the sender's email address
Constants:
    DEFAULT_SENDER (str): The default sender email address to filter the messages.
    DEFAULT_PATH_IN (str): The default input directory path where .msg files are located.
    DEFAULT_PATH_OUT (str): The default output directory path where attachments will be saved.
Usage:
    Run the script directly to process email messages and extract attachments:
    $ python extract_docx.py
"""

import os.path
import re

from extract_msg import Message

DEFAULT_SENDER = "vhaofficeofaushivccommunications@va.gov"
DEFAULT_PATH_IN = "emails"
DEFAULT_PATH_OUT = "attachments"


def _init_data_paths(out_folder, in_folder=None):
    """
    Initializes the data paths by creating the output folder if it doesn't exist
    and ensuring the input folder exists if provided.
    Parameters:
    out_folder (str): The path to the output folder. This folder will be created
        if it does not exist.
    in_folder (str, optional): The path to the input folder. If provided, this
        function will check if it exists.
    """
    # create the output folder if it doesn't exist
    if not os.path.isdir(out_folder):
        os.mkdir(out_folder)

    # make sure the input folder exists
    if in_folder is not None and not os.path.isdir(in_folder):
        print(f"The input folder {in_folder} is required.")


def find_and_save_attachments(msg: Message, save_path):
    """
    Finds and saves .docx attachments from an email message to a specified directory.
    Args:
        msg (Message): The email message object containing attachments.
        save_path (str): The directory path where attachments will be saved.
    Returns:
        None
    Raises:
        OSError: If there is an error saving the attachment.
    Notes:
        - Only attachments with a .docx extension are saved.
        - Attachments are saved with a timestamp appended to their original filename.
        - If an attachment has no filename, it is skipped.
    """
    _init_data_paths(save_path, None)
    _init_data_paths(save_path)
    appr_file_types = [".docx", ".pdf"]

    for attachment in msg.attachments:
        if attachment.longFilename:
            attachment_filename, extension = os.path.splitext(attachment.longFilename)
            if extension in appr_file_types:
                new_filename = f"{attachment_filename}{extension}"
                file_path = os.path.join(save_path, new_filename)

                if not os.path.isfile(file_path):
                    attachment.save(customPath=save_path, customFilename=new_filename)
                    print("Saved attachments:", new_filename)
                else:
                    print("Attachment already exists:", new_filename)
        else:
            print("Skipping attachment with None filename.")


def parse_from_path(
    senders: list = None, path_in=DEFAULT_PATH_IN, path_out=DEFAULT_PATH_OUT
):
    """
    Parses email messages from a specified input directory and processes them
    based on the sender's email address.

    Args:
        senders (list, optional): A list of sender email addresses to filter the messages.
        Defaults to None.
        path_in (str, optional): The input directory path where .msg files are located.
        Defaults to DEFAULT_PATH_IN.
        path_out (str, optional): The output directory path where attachments will be saved.
        Defaults to DEFAULT_PATH_OUT.
    Returns:
        None
    Notes:
        - If the `senders` list is None or empty, it defaults to a list containing `DEFAULT_SENDER`.
        - Only files with a .msg extension in the input directory are processed.
        - Attachments from the emails of the specified senders are extracted and saved to the output
        directory.
    """
    if senders is None or len(senders) == 0:
        senders = [DEFAULT_SENDER]

    out_folder = os.path.join(os.getcwd(), path_out)
    in_folder = os.path.join(os.getcwd(), path_in)

    _init_data_paths(out_folder, in_folder)

    # iterate over all .msg files in the input folder
    for filename in os.listdir(in_folder):
        # skip non-msg files
        if filename.endswith(".msg"):
            print(f"Processing {filename}...")
            file_path = os.path.join(in_folder, filename)
            # extract the email message
            msg = Message(file_path)

            # extract the sender from the email
            match = re.search(r"<(.+?@.+?)>", msg.sender).group(1).lower()

            # check if the sender is in the list of senders
            if match in senders:
                # find and save all attachments
                find_and_save_attachments(msg, out_folder)

                # close the message
                msg.close()

                print("Completed processing:", filename)
            else:
                print(f"Skipping {filename}...")
                continue
