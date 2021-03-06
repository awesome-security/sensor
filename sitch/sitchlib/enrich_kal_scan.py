# import csv
# import gzip
# import json
# import os
import alert_manager
from utility import Utility


class KalScanEnricher(object):
    def __init__(self, kal_threshold):
        self.alerts = alert_manager.AlertManager()
        self.kal_threshold = kal_threshold
        return

    def enrich_kal_scan(self, scan_document):
        results_set = [("scan", scan_document)]
        kal_threshold = float(self.kal_threshold)
        # platform_name = scan_document["scanner_name"]
        if scan_document["scan_results"] == []:
            print("EnrichKal: No results found in scan document...")
            return results_set
        else:
            for result in scan_document["scan_results"]:
                try:
                    msg = {}
                    msg["band"] = result["band"]
                    msg["power"] = Utility.str_to_float(result["power"])
                    msg["sample_rate"] = result["sample_rate"]
                    msg["final_freq"] = result["final_freq"]
                    msg["channel"] = result["channel"]
                    msg["gain"] = result["gain"]
                    msg["site_name"] = scan_document["scan_location"]["name"]
                    msg["scan_start"] = scan_document["scan_start"]
                    msg["scan_finish"] = scan_document["scan_finish"]
                    msg["scan_program"] = scan_document["scan_program"]
                    msg["scanner_public_ip"] = scan_document["scanner_public_ip"]
                    try:
                        msg["arfcn_int"] = int(result["channel"])
                    except:
                        print("EnrichKal: Unable to convert ARFCN to int")
                        print(result["channel"])
                        msg["arfcn_int"] = 0
                    chan_enriched = ('kal_channel', msg)
                    results_set.append(chan_enriched)
                except Exception as e:
                    print("EnrichKal: Failed to enrich Kalibrate message.")
                    print(e)
                    print(msg)
                    # Now we look at alerting...
                try:
                    power = float(msg["power"])
                    if power > kal_threshold:
                        message = "ARFCN %s over threshold at %s" % (
                                  msg["channel"], msg["site_name"])
                        alert = self.alerts.build_alert(200, message)
                        results_set.append(alert)
                except Exception as e:
                    print("EnrichKal: Failed to fire alert!")
                    print(e)
                    print(msg)
        return results_set
