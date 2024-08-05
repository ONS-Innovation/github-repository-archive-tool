# Features File

The feature.json file is used to enable/disable certain features within the app.

## How to Use

To use the features file:

1. Open the features file found at `config/feature.json`.

2. Locate the specific feature you want to enable/disable.

    For example: 
    
    test_data

    ```json
    {
        "features": {
            "test_data": {
                "enabled": true
            }
        }
    }
    ```

3. Set the enabled flag to true or false to opt in/out of the feature.

4. Save the file.

Using feature.json allows developers to hide certain functionality in different deployment environments (i.e removing testing functionality within a production environment).

Changes to feature.json requires a container image rebuild to show during runtime.