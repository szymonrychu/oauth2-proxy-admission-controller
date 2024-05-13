module.exports = {
  "dryRun": null,
  "extends": ["config:recommended", ":rebaseStalePrs"],
  "dependencyDashboard": false,
  "rebaseWhen": "conflicted",
  "suppressNotifications": ["prIgnoreNotification"],
  "username": "szymonrichert.pl bot",
  "gitAuthor": "szymonrichert.pl bot <bot@szymonrichert.pl>",
  "onboarding": false,
  "platform": "github",
  "repositories": ["szymonrychu/oauth2-proxy-admission-controller"],
  "allowedPostUpgradeCommands": ["^.github.*"],
  "allowPostUpgradeCommandTemplating": true,
};
