DROP TABLE IF EXISTS detection;
DROP TABLE IF EXISTS true_positives;
DROP TABLE IF EXISTS false_positives;
DROP TABLE IF EXISTS false_negatives;
DROP TABLE IF EXISTS real_time_detection;
DROP TABLE IF EXISTS real_time_outliers;

CREATE TABLE detection(
    detection_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    detector_name text NOT NULL,
    dataset_name text NOT NULL,
    tn_count int,
    data_size int,
    detection_time float
);

CREATE TABLE true_positives(
    tp_pk INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    detection_id int NOT NULL,
    true_positive_datetime datetime NOT NULL,
    FOREIGN KEY(detection_id) REFERENCES detection(detection_id)
);

CREATE TABLE false_positives(
    fp_pk INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    detection_id int NOT NULL,
    false_positive_datetime datetime NOT NULL,
    FOREIGN KEY(detection_id) REFERENCES detection(detection_id)
);

CREATE TABLE false_negatives(
    fn_pk INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    detection_id int NOT NULL,
    false_negative_datetime datetime NOT NULL,
    FOREIGN KEY(detection_id) REFERENCES detection(detection_id)
);

CREATE TABLE real_time_detection(
    real_time_session_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    real_time_session_name text NOT NULL
);

CREATE TABLE real_time_outliers(
    real_time_outlier_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    real_time_session_id int NOT NULL,
    outlier_datetime datetime NOT NULL,
    outlier_data float NOT NULL,
    FOREIGN KEY(real_time_session_id) REFERENCES real_time_detection(real_time_session_id)
);
