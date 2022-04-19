import pandas as pd

class ensemble_voting:
    """Class containing voting systems for ensemble detection."""

    def get_ensemble_result_majority(all_outliers):
        """
        Outliers determined based on majority of classifications by detectors.

        Parameters:
        all_outliers (list): List of all outlier coordinates returned by each detector.

        Returns:
        dataframe: The final predicitons after voting

        """
        
        all_points_x = []
        all_points_y = []
        predicted_actual_outliers_x = []
        predicted_actual_outliers_y = []
        
        for outlier_data in all_outliers:
            for point_x in outlier_data['timestamp']:
                all_points_x.append(point_x)
            for point_y in outlier_data['data']:
                all_points_y.append(point_y)

        i = 0
        while (i < len(all_points_x)):
            if (all_points_x[i] not in predicted_actual_outliers_x):
                if (all_points_x.count(all_points_x[i]) > 2):
                    predicted_actual_outliers_x.append(all_points_x[i])
                    predicted_actual_outliers_y.append(all_points_y[i])
            i += 1
            
        return pd.DataFrame({'timestamp': predicted_actual_outliers_x,'data': predicted_actual_outliers_y})


    def get_ensemble_result_confidence(detector_results):
        """
        Outliers determined based on combined confidence.

        Parameters:
        all_outliers (list): List of all outlier coordinates with confidence returned by each detector.

        Returns:
        dataframe: The final predicitons after voting

        """

        #print('Starting vote')
        all_points_x = []
        all_points_y = []
        final_confidence = []

        predicted_actual_outliers_x = []
        predicted_actual_outliers_y = []

        # fill all points x and y

        for detector_result in detector_results:
            i = 0
            while (i < len(detector_result['timestamp'])):
                if (detector_result['timestamp'][i] not in all_points_x):
                    all_points_x.append(detector_result['timestamp'][i])
                    all_points_y.append(detector_result['data'][i])
                i += 1
        
        # sum confidences
        i = 0
        while (i < len(all_points_x)):
            current_conf = 0
            for detector_result in detector_results:
                df = detector_result.loc[detector_result['timestamp'] == all_points_x[i]]
                try:
                    current_conf += (df['confidence'].iloc[0])
                except:
                    poina = 0 #do nothing
                    #print("No confidence to add")
            final_confidence.append(current_conf)
            i += 1

        # Return outliers

        i = 0
        while (i < len(final_confidence)):
            if (final_confidence[i] < -0.4):
                print(final_confidence[i])
                predicted_actual_outliers_x.append(all_points_x[i])
                predicted_actual_outliers_y.append(all_points_y[i])
            i += 1

        return pd.DataFrame({'timestamp': predicted_actual_outliers_x,'data': predicted_actual_outliers_y})


