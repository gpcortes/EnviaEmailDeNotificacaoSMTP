from worker import worker
from time import sleep
from smtpmail import SMTPClient
from os.path import expanduser
import javaobj
from base64 import b64decode
import json

worker = worker()

def unserialize(data):
    if data.type_ == 'Object':
        java_obj = b64decode(data.value)
        return javaobj.loads(java_obj)
    elif data.type_ == 'String':
        return [data.value]
    elif data.type_ == 'Json':
        data_list = []
        data_json = json.loads(data.value)
        for index in data_json:
            if 'value' in data_json[index]:
                if data_json[index]['value'] != '':
                    data_list.append(data_json[index]['value'])
        return data_list
    else:
        return data

if __name__ == '__main__':
    print('Worker started')
    while True:
        home = expanduser("~")

        tasks = worker.fetch_tasks(max_tasks=10)

        for task in tasks:
            print('Task {} processing.'.format(task.id_))
            email = SMTPClient()
            email.toAddresses = unserialize(task.variables['toAddresses']) if 'toAddresses' in task.variables else email.toAddresses
            email.bccAddresses = unserialize(task.variables['bccAddresses']) if 'bccAddresses' in task.variables else email.bccAddresses
            email.ccAddresses = unserialize(task.variables['ccAddresses']) if 'ccAddresses' in task.variables else email.ccAddresses
            
            htmlMessage = task.variables['htmlMessage'].value if 'htmlMessage' in task.variables else email.htmlMessage
            if task.variables['htmlMessage'].type_ == 'Json':
                htmlMessage = json.loads(htmlMessage)["message"]
            email.htmlMessage = htmlMessage
            email.textMessage = task.variables['textMessage'].value if 'textMessage' in task.variables else email.textMessage
            email.subject = task.variables['subject'].value if 'subject' in task.variables else email.subject

            document_attache = unserialize(task.variables['document_attache']) if 'document_attache' in task.variables else []

            print(document_attache)

            print('email ---->', task.variables['toAddresses'].value)
            for document_name in document_attache:
                file_path = home + '/outputs/' + document_name
                email.attachments.append(file_path)

            result = email.send()

            if result == False:
                print('Error sending email!')
                del email
                continue
            
            print('Email successfully sent!')
            del email
            worker.complete_task(task_id=task.id_)

        if len(tasks) == 0:
            sleep(30)