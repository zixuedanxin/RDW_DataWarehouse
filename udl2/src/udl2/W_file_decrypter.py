import os

from udl2.celery import celery
from celery.utils.log import get_task_logger
from filedecrypter.file_decrypter import decrypt_file
import udl2.message_keys as mk
from udl2.celery import celery, udl2_conf
from udl2_util.file_util import get_decrypted_dir

__author__ = 'swimberly'

logger = get_task_logger(__name__)


@celery.task(name="udl2.W_file_decrypter.task")
def task(incoming_msg):
    file_to_decrypt = incoming_msg[mk.FILE_TO_DECRYPT]
    passphrase = udl2_conf ['passphrase']
    guid_batch = incoming_msg[mk.GUID_BATCH]
    gpghome = udl2_conf ['gpg_home']
    tenant_directory_paths = incoming_msg[mk.TENANT_DIRECTORY_PATHS]
    decrypt_to_dir = tenant_directory_paths['decrypted']

    logger.info('W_FILE_DECRYPTER: received file <%s> with guid_batch = <%s>' % (file_to_decrypt, guid_batch))
    logger.info('W_FILE_DECRYPTER: Decrypt to <%s>' % decrypt_to_dir)

    status, decrypted_file = decrypt_file(file_to_decrypt, decrypt_to_dir, passphrase, gpghome)
    logger.info('Decrypted file:', decrypted_file)
    logger.info('Decryption status:', status)

    # Outgoing message to be piped to the file expander
    outgoing_msg = {}
    outgoing_msg.update(incoming_msg)
    outgoing_msg.update({mk.FILE_TO_EXPAND: decrypted_file})
    return outgoing_msg
