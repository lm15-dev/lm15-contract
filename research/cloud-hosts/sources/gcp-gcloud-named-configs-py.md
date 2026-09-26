# gcloud CLI 581.0.0 (nixpkgs google-cloud-sdk), excerpts frozen 2026-09-26
# lib/googlecloudsdk/core/config.py and core/configurations/named_configs.py (Apache-2.0).
# Where gcloud keeps the active configuration and its properties file.

## core/config.py:40-50

# Environment variable for the directory containing Cloud SDK configuration.
CLOUDSDK_CONFIG = 'CLOUDSDK_CONFIG'

# Environment variable for overriding the Cloud SDK active named config
CLOUDSDK_ACTIVE_CONFIG_NAME = 'CLOUDSDK_ACTIVE_CONFIG_NAME'


class InstallationConfig(object):
  """Loads configuration constants from the core config file.


## core/config.py:760-790

    Returns:
      str, The path to the file.
    """
    return os.path.join(self.global_config_dir, self.CLOUDSDK_PROPERTIES_NAME)

  @property
  def named_config_activator_path(self):
    """Gets the path to the file pointing at the user's active named config.

    This is the file that stores the name of the user's active named config,
    not the path to the configuration file itself.

    Returns:
      str, The path to the file.
    """
    return os.path.join(self.global_config_dir, 'active_config')

  @property
  def named_config_directory(self):
    """Gets the path to the directory that stores the named configs.

    Returns:
      str, The path to the directory.
    """
    return os.path.join(self.global_config_dir, 'configurations')

  @property
  def config_sentinel_file(self):
    """Gets the path to the config sentinel.


## core/configurations/named_configs.py:28-40

# The special configuration named NONE contains no properties
_NO_ACTIVE_CONFIG_NAME = 'NONE'
_RESERVED_CONFIG_NAMES = (_NO_ACTIVE_CONFIG_NAME,)
# This will be created by default when there are no configurations present.
DEFAULT_CONFIG_NAME = 'default'

_VALID_CONFIG_NAME_REGEX = r'^[a-z][-a-z0-9]*$'
_CONFIG_FILE_PREFIX = 'config_'
_CONFIG_FILE_REGEX = r'^config_([a-z][-a-z0-9]*)$'


class Error(exceptions.Error):

## core/configurations/named_configs.py:465-580
def ActiveConfig(force_create):
  """Gets the currently active configuration.

  There must always be an active configuration.  If there isn't this means
  no configurations have been created yet and this will auto-create a default
  configuration.  If there are legacy user properties, they will be migrated
  to the newly created configuration.

  Args:
    force_create: bool, If False and if there are no legacy properties, the
      new default configuration won't actually be created.  We just pretend
      that it exists, which is sufficient since it is empty.  We do this to
      avoid always creating the configuration when properties are just trying
      to be read.  This should only be set to False when seeing a
      PropertiesFile object.  All other operations must actually create the
      configuration.

  Returns:
    Configuration, the currently active configuration.
  """
  config_name = _EffectiveActiveConfigName()

  # No configurations have ever been created
  if not config_name:
    config_name = _CreateDefaultConfig(force_create)

  return Configuration(config_name, True)


def _EffectiveActiveConfigName():
  """Gets the currently active configuration.

  It checks (in order):
    - Flag values
    - Environment variable values
    - The value set in the activator file

  Returns:
    str, The name of the active configuration or None if no location declares
    an active configuration.
  """
  config_name = FLAG_OVERRIDE_STACK.ActiveConfig()
  if not config_name:
    config_name = _ActiveConfigNameFromEnv()
  if not config_name:
    config_name = _ActiveConfigNameFromFile()
  return config_name


def _ActiveConfigNameFromEnv():
  """Gets the currently active configuration according to the environment.

  Returns:
    str, The name of the active configuration or None.
  """
  return encoding.GetEncodedValue(
      os.environ, config.CLOUDSDK_ACTIVE_CONFIG_NAME, None)


def _ActiveConfigNameFromFile():
  """Gets the name of the user's active named config according to the file.

  Returns:
    str, The name of the active configuration or None.
  """
  path = config.Paths().named_config_activator_path
  is_invalid = False

  try:
    config_name = file_utils.ReadFileContents(path)
    # If the file is empty, treat it like the file does not exist.
    if config_name:
      if _IsValidConfigName(config_name, allow_reserved=True):
        return config_name
      else:
        # Somehow the file got corrupt, just remove it and it will get
        # recreated correctly.
        is_invalid = True
  except file_utils.MissingFileError:
    pass
  except file_utils.Error as exc:
    raise NamedConfigFileAccessError(
        'Active configuration name could not be read from: [{0}]. Ensure you '
        'have sufficient read permissions on required active configuration '
        'in [{1}]'
        .format(path, config.Paths().named_config_directory), exc)

  if is_invalid:
    os.remove(path)
  # The active named config pointer file is missing, return None
  return None


def _FileForConfig(config_name, paths):
  """Gets the path to the properties file for a given configuration.

  The file need not actually exist, it is just the path where it would be.

  Args:
    config_name: str, The name of the configuration.
    paths: config.Paths, The instantiated Paths object to use to calculate the
      location.

  Returns:
    str, The path to the file or None if this configuration does not have a
    corresponding file.
  """
  if config_name == _NO_ACTIVE_CONFIG_NAME:
    return None
  return os.path.join(paths.named_config_directory,
                      _CONFIG_FILE_PREFIX + config_name)


def _IsValidConfigName(config_name, allow_reserved):
  """Determines if the given configuration name conforms to the standard.

