DROP TABLE IF EXISTS detection;
DROP TABLE IF EXISTS true_positives;
DROP TABLE IF EXISTS false_positives;
DROP TABLE IF EXISTS false_negatives;
DROP TABLE IF EXISTS real_time_detection;
DROP TABLE IF EXISTS real_time_outliers;

CREATE TABLE detection(
    detection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    detector_name text,
    dataset_name text,
    tn_count int,
    data_size int,
    detection_time float
);

CREATE TABLE true_positives(
    tp_pk INTEGER PRIMARY KEY AUTOINCREMENT,
    detection_id int,
    true_positive_datetime datetime,
    FOREIGN KEY(detection_id) REFERENCES detection(detection_id)
);

CREATE TABLE false_positives(
    fp_pk INTEGER PRIMARY KEY AUTOINCREMENT,
    detection_id int,
    false_positive_datetime datetime,
    FOREIGN KEY(detection_id) REFERENCES detection(detection_id)
);

CREATE TABLE false_negatives(
    fn_pk INTEGER PRIMARY KEY AUTOINCREMENT,
    detection_id int,
    false_negative_datetime datetime,
    FOREIGN KEY(detection_id) REFERENCES detection(detection_id)
);



CREATE TABLE real_time_detection(
    real_time_session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    real_time_session_name text
);

CREATE TABLE real_time_outliers(
    real_time_outlier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    real_time_session_id int,
    outlier_datetime datetime,
    outlier_data float,
    FOREIGN KEY(real_time_session_id) REFERENCES real_time_detection(real_time_session_id)
);
