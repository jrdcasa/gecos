awk 'NR>5 {print $3" "$4" "$7}' Mol-ia_m1-charge.txt >extracted_middle_charges.txt
