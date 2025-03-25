# Dejavu Setup Guide

This guide provides step-by-step instructions to set up Dejavu for audio fingerprinting, including database configuration and necessary modifications to the `fingerprints` and `songs` tables.

## 1. Install Dependencies
Ensure you have the required dependencies installed before proceeding:

- Python 3.x
- MySQL Server
- Required Python packages (install using `pip install -r requirements.txt`)

## 2. Database Configuration

### 2.1 Create and Configure the Database

1. Log into MySQL:
   ```sh
   mysql -u root -p
   ```

2. Create the database:
   ```sql
   CREATE DATABASE dejavu;
   ```

3. Use the newly created database:
   ```sql
   USE dejavu;
   ```

4. Create the `songs` table:
   ```sql
   CREATE TABLE songs (
       song_id MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT,
       song_name VARCHAR(250) NOT NULL,
       fingerprinted TINYINT DEFAULT 0,
       file_sha1 BINARY(20) NOT NULL,
       total_hashes INT NOT NULL DEFAULT 0,
       date_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
       date_modified DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
       PRIMARY KEY (song_id)
   );
   ```

5. Create the `fingerprints` table:
   ```sql
   CREATE TABLE fingerprints (
       hash BINARY(10) NOT NULL,
       song_id MEDIUMINT UNSIGNED NOT NULL,
       offset INT UNSIGNED NOT NULL,
       date_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
       date_modified DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
       PRIMARY KEY (hash, song_id, offset)
   );
   ```

## 3. Configure Dejavu

Modify the `dejavu.cnf` file (or your equivalent configuration file) to include the correct database credentials:

```json
{
    "database": {
        "host": "localhost",
        "user": "root",
        "password": "yourpassword",
        "database": "dejavu"
    },
    "database_type": "mysql"
}
```

## 4. Run Dejavu

Once the database is set up and configured, you can start fingerprinting audio files:

```sh
python dejavu.py --fingerprint /path/to/audio/files
```

To recognize a song:

```sh
python dejavu.py --recognize file /path/to/query/audio.mp3
```

## Troubleshooting
- Ensure MySQL is running and accessible.
- Double-check database credentials in `dejavu.cnf`.
- Verify that tables are correctly created using `DESCRIBE songs;` and `DESCRIBE fingerprints;`.
- If errors occur, consult the logs for details.

---

Now, Dejavu is ready to use with your modified database schema!

