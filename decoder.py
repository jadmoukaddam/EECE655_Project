import struct

def decode_coap_message(raw_message):
    # Convert the raw message to a byte array if it's a string
    if isinstance(raw_message, str):
        raw_message = bytes(raw_message, 'latin1')

    # Extract the header components
    version_type_token_length, code, message_id = struct.unpack('!BBH', raw_message[:4])

    version = (version_type_token_length >> 6) & 0x03
    type = (version_type_token_length >> 4) & 0x03
    token_length = version_type_token_length & 0x0F

    # Extract the token
    token = raw_message[4:4 + token_length]

    # Process options and payload
    current_index = 4 + token_length
    options = []
    payload = None

    while current_index < len(raw_message):
        # Check for payload marker (0xFF)
        if raw_message[current_index] == 0xFF:
            current_index += 1
            payload = raw_message[current_index:].decode('utf-8', errors='ignore')
            break

        # Parse the option (this is a simplified version and may not handle all cases)
        option_delta = (raw_message[current_index] >> 4) & 0x0F
        option_length = raw_message[current_index] & 0x0F
        current_index += 1

        option_value = raw_message[current_index:current_index + option_length]
        options.append((option_delta, option_value))
        current_index += option_length

    return {
        'Version': version,
        'Type': type,
        'Token Length': token_length,
        'Code': code,
        'Message ID': message_id,
        'Token': token.hex().upper(),
        'Options': options,
        'Payload': payload
    }

# Example usage
message = b'B\x01\x94\xc9\x96\xe1\xb4time'
decoded_message = decode_coap_message(message)
print(decoded_message)
