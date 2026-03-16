#!/usr/bin/env bash
set -euxo pipefail

dir=$( dirname -- "$0"; )/..

cp -Tr "$dir/gatelogue-types-sql" "$dir/gatelogue-types-py/src/gatelogue_types/sql"
rm "$dir/gatelogue-types-py/src/gatelogue_types/sql/copy.sh"
echo "To devs: edit gatelogue-types-sql instead" > "$dir/gatelogue-types-py/src/gatelogue_types/sql/.DO_NOT_EDIT"

cp -Tr "$dir/gatelogue-types-sql" "$dir/gatelogue-types-rs/src/sql"
rm "$dir/gatelogue-types-rs/src/sql/copy.sh"
echo "To devs: edit gatelogue-types-sql instead" > "$dir/gatelogue-types-rs/src/sql/.DO_NOT_EDIT"

cp -Tr "$dir/gatelogue-types-sql" "$dir/gatelogue-types-ts/src/sql"
rm "$dir/gatelogue-types-ts/src/sql/copy.sh"
echo "To devs: edit gatelogue-types-sql instead" > "$dir/gatelogue-types-ts/src/sql/.DO_NOT_EDIT"
