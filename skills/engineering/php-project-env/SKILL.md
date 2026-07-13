---
name: php-project-env
description: Implement and debug PHP project .env loading with vlucas/phpdotenv. Use when the user asks about PHP .env files, phpdotenv, getenv, $_ENV, Docker PHP web roots, or env path under /var/www/data/<project> vs project root.
---

# PHP Project Env

## Path Policy

For projects under `/var/www/html/<project>` (source: `html/<project>/`):

| Context | `.env` path (container) | Source path |
|---------|-------------------------|-------------|
| production / development | `/var/www/data/<project>/.env` | `data/<project>/.env` |
| localhost | `/var/www/data/<project>/.env` if file exists, else `/var/www/html/<project>/.env` | `data/<project>/.env` or `html/<project>/.env` |

Reference: `html/dialogflow/index.php` (after `ENVIRONMENT` is defined).

## Implementation Pattern

Use `vlucas/phpdotenv` via Composer. Load **after** `ENVIRONMENT` is defined, **before** CodeIgniter / app bootstrap.

Replace `<project>` with the folder name (e.g. `dialogflow`).

```php
/*
 * Load project .env (vlucas/phpdotenv via composer)
 * production / development → /var/www/data/<project>/.env
 * localhost → /var/www/data/<project>/.env if exists, else html/<project>/.env
 */
$projectAutoload = __DIR__ . '/vendor/autoload.php';
$dataEnvFile = dirname(dirname(__DIR__)) . '/data/<project>/.env';
$localEnvFile = __DIR__ . '/.env';
$isServerEnv = defined('ENVIRONMENT') && in_array(ENVIRONMENT, array('production', 'development'), true);

if ($isServerEnv) {
    $envFile = $dataEnvFile;
} elseif (is_file($dataEnvFile)) {
    $envFile = $dataEnvFile;
} else {
    $envFile = $localEnvFile;
}

$envLoaded = false;
if (is_file($envFile) && is_file($projectAutoload)) {
    require_once $projectAutoload;
    if (class_exists('Dotenv\\Dotenv')) {
        try {
            Dotenv\Dotenv::createImmutable(dirname($envFile))->safeLoad();
            $envLoaded = true;
        } catch (Throwable $e) {
            error_log('Dotenv load failed: ' . $e->getMessage());
        }
    }
}

if (!$envLoaded && $isServerEnv) {
    error_log('WARNING: .env not loaded. Path: ' . dirname($envFile));
}
```

### createImmutable precedence

`createImmutable` does **not** overwrite variables already in the process environment.

Priority (highest first):

1. Docker / php-fpm / Apache env (set before PHP runs)
2. `.env` file (fills only missing keys)

Safe for production: ops can inject secrets via Docker; `.env` is fallback for local / missing keys.

## Access Pattern

After dotenv loads in `index.php`, config may use `getenv()`:

```php
$config['api_user'] = getenv('API_USER') ?: '';
$config['api_pass'] = getenv('API_PASS') ?: '';
```

`getenv()`, `$_ENV`, and `$_SERVER` all work once dotenv has run. Prefer `getenv()` in CodeIgniter config files loaded after bootstrap.

For verification, only report whether a key exists — never log secret values:

```php
echo 'API_USER loaded=' . (getenv('API_USER') !== false && getenv('API_USER') !== '' ? 'yes' : 'no') . PHP_EOL;
```

## Composer

`composer.json` in project root:

```json
{
  "require": {
    "php": ">=7.0",
    "vlucas/phpdotenv": "^4.3"
  }
}
```

Run `composer install` in `html/<project>/`. Entry point must be `index.php` (or equivalent bootstrap that loads dotenv first).

## Docker

Add volume for externalized env (alongside other `data/*` mounts):

```yaml
volumes:
  - ./html:/var/www/html
  - ./data/<project>:/var/www/data/<project>
```

Verify without exposing secrets:

```bash
docker exec php php -r 'echo "data_env=".(is_file("/var/www/data/<project>/.env") ? "yes" : "no").PHP_EOL; echo "local_env=".(is_file("/var/www/html/<project>/.env") ? "yes" : "no").PHP_EOL; echo "autoload=".(is_file("/var/www/html/<project>/vendor/autoload.php") ? "yes" : "no").PHP_EOL;'
```

## Templates & Git

Commit examples only:

- `html/<project>/.env.example` — localhost fallback template
- `data/<project>/.env.example` — staging / production template

Ignore real secrets:

```gitignore
.env
```

In `html/<project>/.gitignore` ignore project-root `.env`. `data/<project>/.env` lives outside the module repo — manage on server / ops, not in git.

## Checklist

Before saying `.env` cannot load:

- [ ] `ENVIRONMENT` defined before dotenv block
- [ ] Correct `$envFile` for current environment
- [ ] `vendor/autoload.php` exists (`composer install`)
- [ ] Bootstrap goes through `index.php`
- [ ] Docker volume `./data/<project>:/var/www/data/<project>` if using data path locally
