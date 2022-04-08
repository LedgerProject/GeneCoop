# Reinitialize db
if [ -f db.sqlite3 ]
then
    echo "Delete database"
    rm db.sqlite3
fi

find . -name "*000*.py" -exec rm {} \;