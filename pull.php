<?php

require_once 'config.php'; // Edit this file to add repos

$headers = getallheaders();
list($algo, $hash) = explode('=', $headers['X-Hub-Signature'], 2);
$payload = file_get_contents('php://input');
$payloadHash = hash_hmac($algo, $payload, SECRET);
if ($hash !== $payloadHash) {
    exit('Unable To Validate Request, Script Terminated!');
}
$payload = json_decode($payload, true);

$RepoName = $payload['repository']['name'];
$RepoFullName = $payload['repository']['full_name'];
$ref = $payload['ref'];
$private = $payload['repository']['private'];

if (!$private) {
    echo "Private: False\n";
} else {
    echo "Private: True, Credentials Will Be Required!\n";
}

if (isset($Repositories[$RepoName][$ref])) {
    echo shell_exec("./WebServerGitPull.sh '" . $RepoName . "' '" . $Repositories[$RepoName][$ref] . "' 2>&1");
} else if (isset($Repositories[$RepoFullName][$ref])) {
    echo shell_exec("./WebServerGitPull.sh '" . $RepoFullName . "' '" . $Repositories[$RepoFullName][$ref] . "' 2>&1");
} else {
    exit("Repository Not Specified, Script Terminated!");
}

?>
