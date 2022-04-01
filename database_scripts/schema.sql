DROP TABLE IF EXISTS detection;
DROP TABLE IF EXISTS true_positives;
DROP TABLE IF EXISTS false_positives;
DROP TABLE IF EXISTS false_negatives;

CREATE TABLE detection(
    detection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    detector_name text,
    dataset_name text,
    fn_count int,
    data_size int,
    detection_time, float
);

CREATE TABLE true_positives(
    tp_pk INTEGER PRIMARY KEY AUTOINCREMENT,
    detection_id int,
    true_positive_datetime datetime,
    FOREIGN KEY(detection_id) REFERENCES detection(detection_id)
);

CREATE TABLE false_positives(
    tp_pk INTEGER PRIMARY KEY AUTOINCREMENT,
    detection_id int,
    false_positive_datetime datetime,
    FOREIGN KEY(detection_id) REFERENCES detection(detection_id)
);

CREATE TABLE false_negatives(
    tp_pk INTEGER PRIMARY KEY AUTOINCREMENT,
    detection_id int,
    false_negative_datetime datetime,
    FOREIGN KEY(detection_id) REFERENCES detection(detection_id)
);
