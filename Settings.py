class Settings(object):
    ''' Class to handle loading and saving settings for skt-chat client and
    server.

    Reads settings from a config file line by line.  Settings stored as
    'setting:value' strings.

    Reads and edits settings from a dict passed to readConfig or editConfig.
    '''
    def __init__(self, setting_type):
        types = ['server', 'client']
        if setting_type not in types:
            raise ValueError('Settings setting_type must be \'server\' or \'client\'')

        self.setting_type = setting_type

    def readConfig(self, settings_dict):
        ''' Read config file in to settings_dict

        Args:
        settings_dict: dict to load settings in to
        '''
        if self.setting_type == 'server':
            with open('settings.server', 'r') as settings_file:
                lines = settings_file.readlines()
        elif self.setting_type == 'client':
            with open('settings.client', 'r') as settings_file:
                lines = settings_file.readlines()

        for i, curline in enumerate(lines):
            curline = curline.strip().split(':')
            try:
                settings_dict[curline[0]] = curline[1]
            except IndexError:
                print('Invalid line in configuration file: %d: "%s"'%(i,''.join(curline)))


    def editConfig(self, settings_dict, setting, value):
        ''' Edit a single setting in the config file and update settings_dict

        Args:
        settings_dict: dict to operate on
        setting: name of setting, string
        value: value of setting, string
        '''
        # Is set to True if setting is found in file
        setting_match = False

        if self.setting_type == 'server':
            with open('settings.server', 'r') as settings_file:
                lines = settings_file.readlines()
        elif self.setting_type == 'client':
            with open('settings.client', 'r') as settings_file:
                lines = settings_file.readlines()

        # Update setting line
        for i, line in enumerate(lines):
            if line.startswith(setting):
                setting_match = True
                new_line = '%s:%s\n'%(setting,value)
                lines[i] = new_line
                break

        # Setting didn't exist in file, create it
        if not setting_match:
            lines.append('%s:%s\n'%(setting, value))

        settings_dict[setting] = value

        if self.setting_type == 'server':
            with open('settings.server', 'w') as settings_file:
                settings_file.writelines(lines)
        elif self.setting_type == 'client':
            with open('settings.client', 'w') as settings_file:
                settings_file.writelines(lines)
