from yubaoCtrader.trader.utility import PcapFilter, solve_udpcap_header

def callback(content, timestamp_high:int, timestamp_low:int, context):

    udpcap_header, header_length = solve_udpcap_header(content)
    
    if udpcap_header == None:
        return content, False

    if udpcap_header.DestinationPort == 2042 or udpcap_header.DestinationPort == 4042:
        return content, True
    
    else:
        return content, False

if __name__ == '__main__':
    f = PcapFilter("tz_222_20240807.pcap", "A50_222_20240807.pcap", callback, None)
    f.begin()
