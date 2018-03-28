-- Sample pig script to be used in Unit Test Suite

-- for AWS: s3a://${BUCKET}/
-- for GCP: gs://${BUCKET}/
truck_events = LOAD '$TRUCKS_CSV' USING PigStorage(',') AS
                (driverId:int,
                truckId:int,
                eventTime:chararray,
                eventType:chararray,
                longitude:double,
                latitude:double,
                eventKey:chararray,
                correlationId:long,
                driverName:chararray,
                routeId:long,
                routeName:chararray,
                eventDate:chararray);

drivers =  LOAD '$DRIVERS_CSV' USING PigStorage(',') AS
                (driverId:int,
                name:chararray,
                ssn:chararray,
                location:chararray,
                certified:chararray,
                wage_plan:chararray);

join_data = JOIN  truck_events BY (driverId), drivers BY (driverId);

--DESCRIBE join_data;
DUMP join_data;
