import time
import requests  
from api_secrets import API_KEY_ASSEMBLY
import sys

#upload
upload_endpoint="https://api.assemblyai.com/v2/upload"
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
filename=sys.argv[1]
headers ={'authorization': API_KEY_ASSEMBLY}

def upload(filename):

    def read_file(filename,chunk_size=5242880):
        with open(filename,'rb') as file:
            while True:
                data = file.read(chunk_size)
                if not data:
                    break
                yield data

    
    upload_response = requests.post(upload_endpoint,
                            headers=headers,
                            data=read_file(filename))
    

    audio_url=upload_response.json()['upload_url']
    return audio_url


#transcribe 

def transcribe(audio_url):
        
    transcript_request={"audio_url":audio_url}
    transcript_response=requests.post(transcript_endpoint,json=transcript_request,headers=headers)
    
    job_id = transcript_response.json()['id']
    return job_id

audio_url=upload(filename)
transcript_id=transcribe(audio_url)
print(transcript_id)

#poll
def poll(transcript_id):

    polling_endpoint= transcript_endpoint + '/' + transcript_id
    polling_response=requests.get(polling_endpoint,headers=headers)
    print(polling_response.json())
def get_transcription_result_url(audio_url):
    transcript_id= transcribe(audio_url)
    while True:
        data = poll(transcript_id)
        
        if data:
            if data['status'] == 'completed':
                return data, None
            elif data['status'] == 'error':
                return None, data.get('error', 'Unknown error')
            else:
                print(f"Current status: {data['status']}. Polling again in 5 seconds...")
        else:
            return None, 'Failed to retrieve job status.'

        time.sleep(5)  # Delay between polls

# Main execution
audio_url = upload(filename)
data, error = get_transcription_result_url(audio_url)print(data)
