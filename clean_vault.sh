#!/bin/bash

find "AI_Employee_Vault" -mindepth 2 -type f -delete

"" > AI_Employee_Vault/.orchestrator_state.json

echo "The vault has been cleaned, successfully."
