import requests
import json 


class Twist:

    def __init__(self, email: str, password: str):
        self.__TWIST_API_URL = "https://api.twist.com/api/v3"
        try:
            self.login(email, password)
        except Exception as e:
            raise Exception("Failed to initialize Twist:", e)


    def login(self, email: str, password: str):
        try:
            login_response = requests.post(self.__TWIST_API_URL + '/users/login', json = {'email': email, 'password': password})

            if "error_code" in login_response.json():
                raise Exception('Failed to login to Twist:', login_response.json()['error_string'])
            
            self.account = login_response.json()
            self.headers = {'Authorization': f'Bearer {self.account["token"]}'}
        except requests.exceptions.RequestException  as e:
            raise Exception("Request Error:", e)


    def send_get_request(self, url_path: str, params: dict = {}):
        try:
            api_response = requests.get(self.__TWIST_API_URL + url_path, headers=self.headers, params=params)
            api_response.raise_for_status()
            return api_response.json()
        except requests.exceptions.RequestException  as e:
            raise Exception("Request Error:", e)
    

    def get_all_workspaces(self):
        return self.send_get_request('/workspaces/get')


    def get_all_channels_in_workspace(self, workspace_id: int):
        return self.send_get_request('/channels/get', {"workspace_id": workspace_id})
    

    def get_all_threads_in_channel(self, channel_id: int):
        return self.send_get_request('/threads/get', {"channel_id": channel_id})
    

    def get_workspace_by_name(self, workspace_name: str):
        all_workspaces = self.get_all_workspaces()
        # Filters all workspaces to find workspace with specified name
        workspace = list(filter(lambda workspace: workspace['name'] == workspace_name, all_workspaces))
        return workspace[0] if len(workspace) > 0 else None
    

    def get_all_workspace_data(self, name: str):
        '''Gets all workspace channels and threads in each channel'''
        workspace_data = dict()

        workspace = twist.get_workspace_by_name(name)

        if(workspace == None):
            raise Exception('No workspace with name "' + name + '" found')

        workspace_data["workspace"] = workspace
        
        workspace_channels = self.get_all_channels_in_workspace(workspace['id'])
        workspace_data["workspace"]["workspace_channels"] = workspace_channels

        for i in range(0, len(workspace_channels)):
            channel_threads = self.get_all_threads_in_channel(workspace_channels[i]['id'])
            workspace_data["workspace"]["workspace_channels"][i]["channel_threads"] = channel_threads

        return workspace_data
    

    def backup_workspace_data(self, workspace_name: str, file_name: str):
        '''Backups workspace data to a file in JSON format'''
        try:
            workspace_data = self.get_all_workspace_data(workspace_name)
            workspace_data_json = json.dumps(workspace_data, indent = 4)

            backup_file = open(file_name, "w")
            backup_file.write(workspace_data_json)
            backup_file.close()
        except Exception as e:
            raise Exception("Workspace Backup Error:", e)


if __name__ == '__main__':

    # Example usage
    
    EMAIL = "example@mail.com"
    PASSWORD = "password123"
    WORKSPACE_NAME = "Workspace Name"
    BACKUP_FILE_NAME = "backup.json"

    twist = Twist(EMAIL, PASSWORD)
    twist.backup_workspace_data(WORKSPACE_NAME, BACKUP_FILE_NAME)