# CHANGELOG


## v3.3.0 (2025-01-28)

### Bug Fixes

- Update test suite to match behavior of FOSSology 4.4.0
  ([`fb366e6`](https://github.com/fossology/fossology-python/commit/fb366e64ccea6ff1d105640796c25594eae82250))

### Chores

- Update all dependencies
  ([`5f740b8`](https://github.com/fossology/fossology-python/commit/5f740b8283633dbbb91199a403ec534048198252))

- Update supported python versions, add semantic release action
  ([`0730530`](https://github.com/fossology/fossology-python/commit/0730530b8b340e4e4d3bcc802e14c9eaaa9fcad1))

- Update workflows triggers, add PyPi project variable
  ([`2bb2945`](https://github.com/fossology/fossology-python/commit/2bb29458b8cda854ec4d646a8011753758cffe7b))

### Features

- Support jobs/history endpoint
  ([`e347226`](https://github.com/fossology/fossology-python/commit/e3472269e957bd8d5a5ecfe39d17ae1275084d87))


## v3.2.1 (2024-04-08)

### Bug Fixes

- **version**: Use v1 by default until v2 will be released
  ([`dc0e0b7`](https://github.com/fossology/fossology-python/commit/dc0e0b722b649fde87ad345c65c30ff1daa501f3))

### Chores

- **image**: Test against latest fossology build
  ([`91c9ca6`](https://github.com/fossology/fossology-python/commit/91c9ca69dafc0e084f0e4393eaf0ec03fb0c9b43))

- **lint**: Replace flake8, black and isort by ruff
  ([`0c94c10`](https://github.com/fossology/fossology-python/commit/0c94c10d4e2327b845b5daa3f325be8d4879f137))

- **types**: Fix type check errors
  ([`4ae209c`](https://github.com/fossology/fossology-python/commit/4ae209cd65ef9aaeb87ed279b50fab0d47aa2e45))


## v3.2.0 (2024-03-19)

### Features

- **3.2.0**: Upgrade to next minor version
  ([`ba51a85`](https://github.com/fossology/fossology-python/commit/ba51a851cb1fd5dbbba0f9ca978d3284ef89a4ae))

- **v2**: Support API version v2 by default
  ([`5b0725a`](https://github.com/fossology/fossology-python/commit/5b0725a9a12effcf3bbd2a149ad5b976510c912d))


## v3.1.1 (2024-02-16)

### Bug Fixes

- **exceptions**: Instantiate the inherited exception class
  ([`4034864`](https://github.com/fossology/fossology-python/commit/4034864eeb152fa338d04a554727c89db0566449))

- **token**: Call sys.exit if server is not reachable
  ([`db5158a`](https://github.com/fossology/fossology-python/commit/db5158a3098c88619487ef7b85647206b753d75c))

Properly test all reponse scenarios Closes #122

### Chores

- Fix default branch name in doc-deploy action
  ([`6211083`](https://github.com/fossology/fossology-python/commit/6211083f27ee55a8fc42e7270116a7c896e39a50))

- **poetry**: Update all dependencies
  ([`41e3883`](https://github.com/fossology/fossology-python/commit/41e3883af16c18d537c66309ee0bf54207ad9b45))

- **tests**: Update to latest Fossology release
  ([`61d76e8`](https://github.com/fossology/fossology-python/commit/61d76e8f7ed0c4ffdf3dbf3e247925c0c6ec371a))

Don't verify item.meta_info since it delivers new data

### Documentation

- Add missing docs chapters
  ([`5992d3c`](https://github.com/fossology/fossology-python/commit/5992d3c414c7dc56b22038dbe0c48da11864aa4e))

- **readme**: Correct import and add hint about the correct Fossology URL
  ([`899c006`](https://github.com/fossology/fossology-python/commit/899c006de9f06fa9fc6be9d989407c531fefaff3))

Closes #124

### Features

- **release**: New patch version 3.1.1
  ([`24b8e5e`](https://github.com/fossology/fossology-python/commit/24b8e5eac8c593d65a386512fa99d849751ad0af))


## v3.1.0 (2023-12-19)

### Bug Fixes

- **tests**: Adapt all tests to API version 1.5.1
  ([`1f03171`](https://github.com/fossology/fossology-python/commit/1f031716855380167c9d4242359fb81f7b044247))

### Chores

- **tests**: Update version of Fossology under test
  ([`3d221a2`](https://github.com/fossology/fossology-python/commit/3d221a218f9c0321fe7af8c6482e81829a11e728))

- **types**: Fix mypy errors
  ([`4884315`](https://github.com/fossology/fossology-python/commit/48843155868569f51cdf142e35726b6e4d87d0bc))

- **update**: Create new minor release
  ([`e53d496`](https://github.com/fossology/fossology-python/commit/e53d4969653db490fd1081b4d58ef30597e8538e))

- **updates**: Python dependencies + fossology version
  ([`53387d0`](https://github.com/fossology/fossology-python/commit/53387d0e561f6cda9dcb01aa6ca63ba2a6373f30))

### Features

- **clearing**: Add bulk clearing endpoints, refactor objects
  ([`ec8155f`](https://github.com/fossology/fossology-python/commit/ec8155f5f85325df55558b5e66713f7dba5adf3d))

- **items**: Prepare new item endpoints for the next release
  ([`a683414`](https://github.com/fossology/fossology-python/commit/a6834140369d7433dcdf14e59076564925a45003))

- **latest**: Test against latest, enable all valid tests
  ([`876a9b6`](https://github.com/fossology/fossology-python/commit/876a9b6ed3127aafe080e6021675f16a78b5d4cb))

- **v2**: Update to API v2.0.0
  ([`008f26c`](https://github.com/fossology/fossology-python/commit/008f26c1a11edb531562377a0f643de44e32d1e9))


## v3.0.0 (2023-08-09)

### Bug Fixes

- **search**: Add hint about feature availability
  ([`96d3d7d`](https://github.com/fossology/fossology-python/commit/96d3d7de161989dc5739ce31e95011ba31fb82dc))

### Chores

- **mypy**: Add mypy dependencies and check
  ([`02c4070`](https://github.com/fossology/fossology-python/commit/02c4070ad9e7e01744a2bb60fa7c89988b8ef8c3))

- **poetry**: Add types-requests
  ([`93b1f0f`](https://github.com/fossology/fossology-python/commit/93b1f0ff4f046da58e2db97cb7b843262c37e065))

- **python**: Update dependencies, use group flag, update actions
  ([`96d74ff`](https://github.com/fossology/fossology-python/commit/96d74ffe1e9ad3c4bf0ab1cbf69ae2f187e3b5d2))

- **release**: Update version string to 3.0.0
  ([`0a04bf4`](https://github.com/fossology/fossology-python/commit/0a04bf459b8b04b09a5a1de398dcbf7144a29974))

- **tests**: Remove compatibility test with version 4.1.x
  ([`194c76f`](https://github.com/fossology/fossology-python/commit/194c76fca945c79507839d6e5d4359defb6eab9a))

### Features

- **download**: Dowload upload by id
  ([`42dd18b`](https://github.com/fossology/fossology-python/commit/42dd18bcb24eb3a3a1115d660f427855e31396a7))

- **groups**: Delete group and manage members
  ([`5a2c33f`](https://github.com/fossology/fossology-python/commit/5a2c33f942778d4cc905a149d453e8bac900ac12))

Breaking change: Fossology doesn't provide reliable API version strings anymore. Remove version
  checks for all groups endpoints.

- **upload**: Change and retreive permissions
  ([`4506b88`](https://github.com/fossology/fossology-python/commit/4506b88619386cfd46f01f055b2b55785492b69c))

- **uploads**: Add all copyrights related endpoints, refactor test files
  ([`db3c2e7`](https://github.com/fossology/fossology-python/commit/db3c2e76355baefc525cb9956ac6649a6a8bb10d))

- **user**: Add default_group information
  ([`b880bd5`](https://github.com/fossology/fossology-python/commit/b880bd5310c2bc75b669b66b4eb698a3e7dd4399))

### Refactoring

- **all**: Update copyright and remove deprecated functions
  ([`1e639aa`](https://github.com/fossology/fossology-python/commit/1e639aa4f539312a0c39cbc9377e7234589e19da))

- **authorization**: Slightly change authorization error logic
  ([`532b1e0`](https://github.com/fossology/fossology-python/commit/532b1e00d9f3a36be8d50d9e5fc4d6d2b624266d))

- **jobs**: Add new /all endpoint, increase timeout robustness
  ([`4b3216f`](https://github.com/fossology/fossology-python/commit/4b3216f310f2c2f426e17ef3d1949851c052ba8a))

- **types**: Fix mypy errors
  ([`0ee397e`](https://github.com/fossology/fossology-python/commit/0ee397e0ffb9e4117ec09625427abc2bb5f7c833))

- **versions**: Get rid of version checking logic (breaking change)
  ([`3db7bf2`](https://github.com/fossology/fossology-python/commit/3db7bf2f29f4f35ae25ab85f577c25845ef618d8))


## v2.1.0 (2023-03-23)

### Bug Fixes

- **uploads**: Set correct uploadType for file
  ([`386fd35`](https://github.com/fossology/fossology-python/commit/386fd35759db40025929d23820ae6dc69dce9b8c))

### Chores

- **action**: Update deploy-to-github-pages
  ([`d3cd9c8`](https://github.com/fossology/fossology-python/commit/d3cd9c8991bfd0c75774031692080fa65f71cd87))

- **deps**: Bump certifi from 2022.9.14 to 2022.12.7
  ([`0742a95`](https://github.com/fossology/fossology-python/commit/0742a9559f63b27d95322de1197c8c1e04873852))

Bumps [certifi](https://github.com/certifi/python-certifi) from 2022.9.14 to 2022.12.7. - [Release
  notes](https://github.com/certifi/python-certifi/releases) -
  [Commits](https://github.com/certifi/python-certifi/compare/2022.09.14...2022.12.07)

--- updated-dependencies: - dependency-name: certifi dependency-type: indirect

...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump setuptools from 65.3.0 to 65.5.1
  ([`2a30904`](https://github.com/fossology/fossology-python/commit/2a3090469e45887530b781ebecb52a9a93f8fe91))

Bumps [setuptools](https://github.com/pypa/setuptools) from 65.3.0 to 65.5.1. - [Release
  notes](https://github.com/pypa/setuptools/releases) -
  [Changelog](https://github.com/pypa/setuptools/blob/main/CHANGES.rst) -
  [Commits](https://github.com/pypa/setuptools/compare/v65.3.0...v65.5.1)

--- updated-dependencies: - dependency-name: setuptools dependency-type: indirect

...

Signed-off-by: dependabot[bot] <support@github.com>

- **poetry**: Update dependencies
  ([`d8d4dcf`](https://github.com/fossology/fossology-python/commit/d8d4dcfee3d7e3e831e1d4fdd7b7711ed4b38309))

### Features

- Add download badge in the README
  ([`edb3f71`](https://github.com/fossology/fossology-python/commit/edb3f718f85e3baa41aa24a69ceebbccc9067ea1))

- **2.1.0**: Prepare for new release
  ([`0a6f8ff`](https://github.com/fossology/fossology-python/commit/0a6f8ff5e3ce9b2ec54b992137e5bc8e6ca290a5))

- **members**: Add more users & group members API calls
  ([`b70744d`](https://github.com/fossology/fossology-python/commit/b70744d61e0d9c05643da726972326f3c7820ad7))

### Refactoring

- **modules**: Move Search and Users classes to dedicated files
  ([`3b19555`](https://github.com/fossology/fossology-python/commit/3b1955566c79d8e76d116dae7b8ef3fea1bcc0f5))


## v2.0.0 (2022-09-22)

### Bug Fixes

- **jobs**: Create JobStatus, improve typing in jobs class
  ([`3fe9bad`](https://github.com/fossology/fossology-python/commit/3fe9bad5632e1fdfc1bf99b85f2f6520337c4bed))

Extent testsuite to only create jobs when needed, verify jobs are completed in the fixture already.

### Chores

- **actions**: Set latest fossology tests to continue-on-error
  ([`4ac5b2a`](https://github.com/fossology/fossology-python/commit/4ac5b2a4f010bd9baba9871c08ef8d3061cffb2d))

- **actions**: Use Python 3.10 by default, upgrade Fossology version
  ([`652011e`](https://github.com/fossology/fossology-python/commit/652011e7c20dc062a81d9659cd4ef34054da503a))

- **update**: Major update 2.0.0
  ([`5b4b4f2`](https://github.com/fossology/fossology-python/commit/5b4b4f24eeb7e1546d6a467b27b05ba992524301))

### Features

- **cli**: Add delete commands and use them in the tests
  ([`ca42bfa`](https://github.com/fossology/fossology-python/commit/ca42bfaf10deb960011dfdd4260f5bb0bff87b5b))

- **next**: Add new features until API 1.4.3, improve tests
  ([`b5775a9`](https://github.com/fossology/fossology-python/commit/b5775a9b32d3b01c92bb775fc4ca33357227cf1a))

- **sample**: Delete upload and file created during the test
  ([`042740a`](https://github.com/fossology/fossology-python/commit/042740a3e3357db612341e1b21e74538e5f0d248))


## v1.5.0 (2022-04-22)

### Bug Fixes

- **report**: Improve content type robustness
  ([`1060c6a`](https://github.com/fossology/fossology-python/commit/1060c6aa6de373d512da6deecd7c9e139303647c))

- **tests**: Rename test folders to avoid conflicts
  ([`976eabe`](https://github.com/fossology/fossology-python/commit/976eabe733c7447e0ae7d67954f8269268e38fe8))

### Chores

- **black**: Fix formating
  ([`71418c0`](https://github.com/fossology/fossology-python/commit/71418c034ac21f63a6099240ffb9da13e185d7ee))

- **deps**: Update dependencies
  ([`45bfb56`](https://github.com/fossology/fossology-python/commit/45bfb56cd8feb675ca66e150010370e87475a501))

- **format**: Apply new black rules
  ([`28693f2`](https://github.com/fossology/fossology-python/commit/28693f269b8abc57d7ec811f7036400baf30052e))

- **version**: Minor upgrade, support Fossology 1.4.0
  ([`cb4adc0`](https://github.com/fossology/fossology-python/commit/cb4adc0e2d83f819a0f5d8c94bca6dd2e9f4a7d6))

- **version**: New patch version
  ([`b3b485f`](https://github.com/fossology/fossology-python/commit/b3b485fb1530f0ae13969edae2f9ca40818ee324))

### Features

- **report**: Add wait_time option to custome report retry delay
  ([`97950f8`](https://github.com/fossology/fossology-python/commit/97950f81751e95af1ba256d0cd655a8d25173e36))

- **upload**: Breaking change for PUT and PATCH /upload methods
  ([`e281d03`](https://github.com/fossology/fossology-python/commit/e281d03556605bb2b7559568f8d4d4ac86d8e26d))


## v1.4.0 (2021-10-07)

### Bug Fixes

- Add missing parameter
  ([`56dbfc9`](https://github.com/fossology/fossology-python/commit/56dbfc941c2cacce14c21440a51c45f375cacd87))

- Unexisting attribute
  ([`3cdb5d4`](https://github.com/fossology/fossology-python/commit/3cdb5d4625953bd495769c4a19bf11a07bb354c2))

- **auth**: Use username for old API versions
  ([`93aa5f8`](https://github.com/fossology/fossology-python/commit/93aa5f89f0c5e688d4da6a1a10d9576d303fec30))

- **README**: Add suggestion from MR
  ([`1356fbe`](https://github.com/fossology/fossology-python/commit/1356fbeeffaaf1c2e4991c9e491ccc954853f3e7))

### Chores

- Create new version 1.4.0
  ([`6f7a20a`](https://github.com/fossology/fossology-python/commit/6f7a20a7239f3e5de3b93683e70eba43fa24fe58))

- Reduce complexity of list_uploads, sort imports
  ([`b8a57f9`](https://github.com/fossology/fossology-python/commit/b8a57f954c7f15138f4849aa5aeae0118dd7a443))

- Run testsuite on last release 3.11.0
  ([`9f6e165`](https://github.com/fossology/fossology-python/commit/9f6e1659e4f8b9b35c210215a08c66e358e8d286))

- **actions**: Run only on given paths changes
  ([`1f14ac8`](https://github.com/fossology/fossology-python/commit/1f14ac8a5eda050eaebecec536844062198bbd56))

fix(pytest): correct module import main

fix(sample): typo

- **ci**: Expand CLI tests to latest stable release
  ([`fe30573`](https://github.com/fossology/fossology-python/commit/fe30573480ab3577d5e71a1cb7faa856cdfa634d))

Only run foss_cli tests on all branches containing the string 'cli'. Update python depdendencies and
  add shpinx and rstcheck dev packages.

- **git**: Update ignore file list
  ([`1106ef6`](https://github.com/fossology/fossology-python/commit/1106ef6fa42bd500b25f3629b23091a81d70a088))

- **pip**: Update dependencies
  ([`aa9acd4`](https://github.com/fossology/fossology-python/commit/aa9acd428c5868efac193c2ced85b8ca2c547cc5))

- **poetry**: Update packages and lock file
  ([`d6c179c`](https://github.com/fossology/fossology-python/commit/d6c179cdd8ff658df69ed745740eeca5b873c398))

- **release**: Prepare for relelase 1.3.4
  ([`02ad244`](https://github.com/fossology/fossology-python/commit/02ad2446245d58314bc36af6cf98b8ee82e7a482))

### Code Style

- Sort imports
  ([`dc63850`](https://github.com/fossology/fossology-python/commit/dc63850f718dff052d168a14a82cad2e49ab6c3f))

### Documentation

- Improve readibility of enums' values, closes #65
  ([`b609e7d`](https://github.com/fossology/fossology-python/commit/b609e7da3b4ca786a3e1797b221ad62e742ae152))

- **badge**: Update name of the test
  ([`385944f`](https://github.com/fossology/fossology-python/commit/385944f5118169fc59f9ae212594e194b9b3c616))

### Features

- Add new upload parameters for version 1.3.4, related to #52
  ([`6adf3ac`](https://github.com/fossology/fossology-python/commit/6adf3ac14f7819e7e420d070138a3376303af183))

- New info and health endpoints
  ([`1b2e571`](https://github.com/fossology/fossology-python/commit/1b2e571e5e5acf39775888e45f8c7e7119c2a3f5))

- **cli**: Polish documentation and help menus
  ([`30ffdb3`](https://github.com/fossology/fossology-python/commit/30ffdb3bbabda6088bc358f7ee02fd04e9e6c370))

Rename 'schedule_jobs' command into 'start_workflow'.


## v1.3.4 (2021-07-23)

### Bug Fixes

- **license**: Type of response changed since 1.3.0
  ([`69d2765`](https://github.com/fossology/fossology-python/commit/69d276557b9f0ff50456ac82f048a33535b25e7a))

- **uploads**: Specify 'group' parameter in call to detail_upload
  ([`9a7dd0a`](https://github.com/fossology/fossology-python/commit/9a7dd0ae4cca2ec26463ba0dbf37c8632df779f9))

### Chores

- **format**: Correct formatting
  ([`e9049d0`](https://github.com/fossology/fossology-python/commit/e9049d0b415cbe287126555ceff2d8176990da56))

- **tests**: Upgrate last release version
  ([`50a4aca`](https://github.com/fossology/fossology-python/commit/50a4aca4d780baba88c2ae04dab2166080c742b6))

### Features

- **jobs**: Add missing reuse options
  ([`9c069df`](https://github.com/fossology/fossology-python/commit/9c069dfa6fea6b937e435c7e48179adb445f3fa8))

- **license**: License endpoint now returns a list
  ([`e78daaa`](https://github.com/fossology/fossology-python/commit/e78daaa78cf339049e95fc1b8123c0e99099afa0))

- **license**: Update license endpoints
  ([`42a669d`](https://github.com/fossology/fossology-python/commit/42a669d6462316ba5a933676cb0f483fdc11de79))

Only support endpoint starting from version 1.3.0 Support GET/POST/PATCH inclusive listing all
  licenses using 'all_pages' argument.

- **self**: Add support for /users/self endpoint
  ([`e767f28`](https://github.com/fossology/fossology-python/commit/e767f28fcd68c9d1112cd5775fc71472921c47a3))

Verify compatibility with older API versions. Update method call examples and tests. Add deprecation
  comment for the user name option.

### Testing

- **jobs**: Fix assertions
  ([`e4dc0ed`](https://github.com/fossology/fossology-python/commit/e4dc0ed2e02eee15d9f28320e50c5aeb459c891e))


## v1.3.3 (2021-04-24)

### Bug Fixes

- **folders**: Compare folders case insensitive
  ([`7bfa058`](https://github.com/fossology/fossology-python/commit/7bfa0588f99bb010f033477c4c9edc35d2dcd53f))

- **folders**: Parent folder id comes with the HTTP response
  ([`5b8ba74`](https://github.com/fossology/fossology-python/commit/5b8ba7469885a2dedfa40a62ba9f2f61c8f64ff7))

- **folders**: Verify duplicate folder is in the same parent
  ([`bffc11c`](https://github.com/fossology/fossology-python/commit/bffc11cb03e3746844257dfceefe32cccacd8657))

### Chores

- **version**: Update patch version
  ([`557ded1`](https://github.com/fossology/fossology-python/commit/557ded1565708f12241bd022d03d41c1706bcf17))

### Features

- **cd**: Build and deploy doc pages using GHA
  ([`0d1f6d9`](https://github.com/fossology/fossology-python/commit/0d1f6d9a625b3bfddc66754057c6abfbfce9bc6b))

Use GitHub Actions to build and deploy documentation pages.

Signed-off-by: Gaurav Mishra <mishra.gaurav@siemens.com>


## v1.3.1 (2021-02-24)

### Bug Fixes

- **report**: Return correct report content as binary
  ([`429164f`](https://github.com/fossology/fossology-python/commit/429164fca7b19e87333ca96919c2a6eea9b0b895))


## v1.3.0 (2021-02-10)

### Features

- **pagination**: Get all_pages for jobs and uploads
  ([`6557ba3`](https://github.com/fossology/fossology-python/commit/6557ba3181401667954687dcf371f97701b4a6da))


## v1.2.1 (2021-01-29)

### Bug Fixes

- **actions**: Rename job only with accepted characters, differentiate tests
  ([`62a431a`](https://github.com/fossology/fossology-python/commit/62a431a884177d21cd96c7ea3357c91588d777f2))

- **groups**: Use global import to fix circular imports issue
  ([`33ac2f1`](https://github.com/fossology/fossology-python/commit/33ac2f12cb8287db3cf261de60c2f9d425061b33))

- **tests**: Skip folder listing assert for 1.0.16
  ([`cbd82c3`](https://github.com/fossology/fossology-python/commit/cbd82c31fb288e5d3d74b242135e5dc756b2a325))

### Chores

- **1.1.0**: Create new minor version
  ([`be6c700`](https://github.com/fossology/fossology-python/commit/be6c70077096b6802d34e6645993f04f08bb69cf))

- **deps**: Update
  ([`914742f`](https://github.com/fossology/fossology-python/commit/914742f515143d07639861ca909df9d1aefadef3))

- **isort**: Sort imports black style
  ([`d505a30`](https://github.com/fossology/fossology-python/commit/d505a30287fc0de98e92331cd08ba62a8956da2e))

### Features

- **backward**: Support API versions >= 1.0.16
  ([`f62ef64`](https://github.com/fossology/fossology-python/commit/f62ef647c0c7d2f5689dbef0c5c3fd71ca3c813d))

- **copyright**: Get copyright from scan
  ([`b93a441`](https://github.com/fossology/fossology-python/commit/b93a44170c5ef5c249a5d48655be25addc1572f7))

Additionally reduce number of tests to shorten the testsuite a bit

- **groups**: Add groups endpoint, increase lib version
  ([`9b0d38b`](https://github.com/fossology/fossology-python/commit/9b0d38bea464e6628a757e32d0993ec3e97b90ec))

- **license**: Add support for new endpoint
  ([`fa23d77`](https://github.com/fossology/fossology-python/commit/fa23d77691a9f922d8d1a1bff25893ababd48ad9))

- **release**: Update deps and prepare release 1.2.1
  ([`1721d72`](https://github.com/fossology/fossology-python/commit/1721d727927353c39d111a88b37027ebeedefb9c))

### Testing

- **backward**: Against lastest and fossology-3.9.0
  ([`b5d8036`](https://github.com/fossology/fossology-python/commit/b5d803609b2386896855ae7665dc608230c64bc5))

- **upload**: Add test-case for server upload
  ([`4be6397`](https://github.com/fossology/fossology-python/commit/4be63976ae68f7b991d0352fc3639bd51df54daa))


## v1.0.0 (2020-12-31)

### Bug Fixes

- **1.1.0**: Minor issues during tests
  ([`e044610`](https://github.com/fossology/fossology-python/commit/e0446102b31d04e71b8043ce52162987df843419))

- **format**: Refactor using black
  ([`a965354`](https://github.com/fossology/fossology-python/commit/a9653540a5cd6fbca70c5f684ea939c0b9406d12))

- **test**: Use request mocks to improve coverage
  ([`4048038`](https://github.com/fossology/fossology-python/commit/4048038823f3597630452736f88483017fd65940))

- **uploads**: Use default x-total-pages value
  ([`5d4fdec`](https://github.com/fossology/fossology-python/commit/5d4fdec4c6805bc044ac6272ad7e05a33ba7af5a))

### Chores

- **1.0.0**: Update version in docs, update copyright
  ([`348f88b`](https://github.com/fossology/fossology-python/commit/348f88bf26786dad72ad6d1797eabf387dc61c8d))

- **poetry**: Update dependencies
  ([`47c6c66`](https://github.com/fossology/fossology-python/commit/47c6c665d5ab941fb5d33a4de8e3b5017272e1c5))

### Documentation

- **readme**: Fix wrong formatting
  ([`c38abca`](https://github.com/fossology/fossology-python/commit/c38abcaea507f8ef93aa2901aa6078977bfa2df1))

- **tags**: Document how to create tags
  ([`a38cb80`](https://github.com/fossology/fossology-python/commit/a38cb806c826b7c3e11e13c45489958be16ebc5f))

### Features

- **api**: Support version 1.1.0
  ([`61709ef`](https://github.com/fossology/fossology-python/commit/61709efb69ee4ed481952ebd462bc6c160073b18))

feat(0.1.2): align with API version 1.0.17

- **api**: Update to support version 1.1.1
  ([`13ba3f0`](https://github.com/fossology/fossology-python/commit/13ba3f0cf661e40c22f96bd1aac669c831bcef72))

- **docs**: Update testsuite call
  ([`3b68966`](https://github.com/fossology/fossology-python/commit/3b68966969e32f721ba3d86b14e282e6e11bf31c))

- **group**: Use header groupName wherever possible, handle 403
  ([`4e55cee`](https://github.com/fossology/fossology-python/commit/4e55cee9cf993a8188aaa0dac7e96a707a00b5cd))

### Refactoring

- **tests**: Use pytest instead of unittest
  ([`83f9093`](https://github.com/fossology/fossology-python/commit/83f9093843a6de080032bacedeb82252dc18ef04))


## v0.2.0 (2020-10-16)

### Refactoring

- **0.2.0**: Get report name from HTTP header
  ([`04ca22d`](https://github.com/fossology/fossology-python/commit/04ca22d7de6b70654b85315ce408fb71acc63a8f))

Interface change for `download_report`: - only the report id is accepted as parameter - removed
  `as_zip` option, Fossology only returns uncompressed reports - return a tuple of the report
  content and the file name as returned by the HTTP GET reponse header - use typehints and fix
  exceptions descriptions


## v0.1.4 (2020-10-14)

### Chores

- **update**: Test with python 3.9, update deps
  ([`df4450c`](https://github.com/fossology/fossology-python/commit/df4450c9d71ce780eb62d12c1f69014b8d324e4c))

- **version**: Add newest patch release to docs
  ([`9f4b265`](https://github.com/fossology/fossology-python/commit/9f4b26507ab0472e522f3af762a4a866ea3b9db3))

- **version**: Update patch release number
  ([`59ff2b2`](https://github.com/fossology/fossology-python/commit/59ff2b21566cb77d70d296dbb61bc737fe1335a2))

### Features

- **upload**: Add wait_time option, improve docstrings
  ([`a32958a`](https://github.com/fossology/fossology-python/commit/a32958af3432c5ec308b118396b935f9d987a820))


## v0.1.3 (2020-09-28)

### Chores

- **poetry**: Update dependencies
  ([`ebf440e`](https://github.com/fossology/fossology-python/commit/ebf440ef250aceb6966695f63127af6c769f2579))

### Features

- **0.1.2**: Align with API version 1.0.17
  ([`a7dbf59`](https://github.com/fossology/fossology-python/commit/a7dbf590529d28c343be83e943aaaad9b046a3ee))

- **group**: Use header groupName wherever possible, handle 403
  ([`e836986`](https://github.com/fossology/fossology-python/commit/e8369867fd50997d0601503e5742a7f9356215d6))

- **release**: Patch version 0.1.3 with reverted commits
  ([`0bf248d`](https://github.com/fossology/fossology-python/commit/0bf248d4eb928e2c870563b182a8b13cd249c901))

- **release**: Update patch release version
  ([`7c5fd37`](https://github.com/fossology/fossology-python/commit/7c5fd371777093934e29b765769d83daa540ff53))

- **uploads**: Honor Retry-After header from GET uploads
  ([`b513e72`](https://github.com/fossology/fossology-python/commit/b513e72587ab03794d6e59adb85b5562a903587c))


## v0.1.1 (2020-06-25)

### Bug Fixes

- **black**: Update format
  ([`b9732e9`](https://github.com/fossology/fossology-python/commit/b9732e9c68c199ba473643f6cbd642d3ebf00ecd))

- **python**: Support 3.6, 3.7 and 3.8
  ([`d7aa374`](https://github.com/fossology/fossology-python/commit/d7aa374661377da8b559110c32846fd994d35940))

### Chores

- **poetry**: Update depedencies
  ([`c0437b7`](https://github.com/fossology/fossology-python/commit/c0437b75170ec7dc2281efda6e53f7a6a01d6775))

### Features

- **release**: Update package version to 0.1.1
  ([`7219bcc`](https://github.com/fossology/fossology-python/commit/7219bccf9e8c0cbb08473c79ea910d79ce829bc7))

- **update**: Support version 1.0.16
  ([`97e7293`](https://github.com/fossology/fossology-python/commit/97e72939afaf981220c5b0372edf4a3df843bbd9))

Add switch to support URL upload and document the different upload types: file, VCS and URL.

Add upload SHA and improve compatibility with future API objects by using keyword arguments.

### Testing

- **sha1**: Add test assertion
  ([`f969411`](https://github.com/fossology/fossology-python/commit/f96941195527db8e5d3701b0a9dd4a3d692feb72))


## v0.1.0 (2020-05-06)

### Bug Fixes

- **action**: Use CODECOV_TOKEN
  ([`f2bacce`](https://github.com/fossology/fossology-python/commit/f2baccec096b4efa08befdde1bebb5427060657f))

- **codecov**: Use bash uploader
  ([`4cf5e0e`](https://github.com/fossology/fossology-python/commit/4cf5e0eb57e90b98a5c0f3d25785162c3e7ea4a6))

- **exception**: Catch JSONDecode error
  ([`3e0f352`](https://github.com/fossology/fossology-python/commit/3e0f352977ce8be6c2ab4f8514817f2e47419987))

- **exceptions**: Return error message from server
  ([`6c08872`](https://github.com/fossology/fossology-python/commit/6c0887299f0c9cacddac09ec7c15e25d39e3cb59))

- **format**: Run black on all remaining files
  ([`4a18f75`](https://github.com/fossology/fossology-python/commit/4a18f75ba3d56b7e754994a908623d3e80002bb9))

### Chores

- **pypi**: Update pyflakes to fully support Python 3.8
  ([`56d3578`](https://github.com/fossology/fossology-python/commit/56d3578aa5ce067d5580c5a2a272efb2d33c5629))

Additionally add codecov and update github action to send report.

- **python**: Adapt to CI environment, run on every commit/pr
  ([`27dace4`](https://github.com/fossology/fossology-python/commit/27dace4e19c6ec9711be47f1f972f7cb038ff286))

### Documentation

- **theme**: Add minor theme modifications
  ([`a75b960`](https://github.com/fossology/fossology-python/commit/a75b9606659e89e11a8f2553817ec33c39ae5718))

### Features

- **api**: Support API version 1.0.13
  ([`3709272`](https://github.com/fossology/fossology-python/commit/37092720df035c5bdbcadd259106cc9b3183e386))

Fix some minor error in previous version Closes #21

- **copyright**: Update year 2020
  ([`2d96cf3`](https://github.com/fossology/fossology-python/commit/2d96cf3db2bb5f33ed260275d029900d562f111c))

- **coverage**: Improve coding style and code coverage
  ([`cfdcd45`](https://github.com/fossology/fossology-python/commit/cfdcd4512d7ed767566a55ec52aca12baddc4613))

- **coverage**: Integrate test coverage
  ([`7f56342`](https://github.com/fossology/fossology-python/commit/7f563423230d9f4a12bb770cb8742d7fd789497f))

### Refactoring

- **partial**: Improve test coverage and fix bugs/style
  ([`045b68f`](https://github.com/fossology/fossology-python/commit/045b68f7e28bbe2867686edaba61d59ddba37999))

- **style**: Fix styling/linting errors
  ([`65cd591`](https://github.com/fossology/fossology-python/commit/65cd59114e9deedfdade09e77296467287fffe66))


## v0.0.11 (2020-03-30)

### Bug Fixes

- **agents**: Add patent agent
  ([`c425974`](https://github.com/fossology/fossology-python/commit/c425974518e610b3dd5bf92ee6a5434066f9a115))

- **agents**: Use **kwargs for additional specific agents
  ([`be6caaa`](https://github.com/fossology/fossology-python/commit/be6caaac5cfb37e84ce84c471d660c6dd11d090d))

- **black**: Reformat using black
  ([`2e9f4f1`](https://github.com/fossology/fossology-python/commit/2e9f4f1a29ff282a934d5fdd541c9409e4ef9408))

- **report**: Update to latest API version
  ([`cce1b33`](https://github.com/fossology/fossology-python/commit/cce1b33075f93e174380890e7d769b6e8097988d))

- **summary**: Ui-less upload summary
  ([`0aca064`](https://github.com/fossology/fossology-python/commit/0aca064bb91cc4a6ecbd550e8b21d81d13c1e6c3))

### Chores

- **0.0.8**: New version
  ([`c444594`](https://github.com/fossology/fossology-python/commit/c44459489bcd184931396754ec785ce8b6081e0d))

- **actions**: Trigger if source or tests are changed
  ([`c686b9d`](https://github.com/fossology/fossology-python/commit/c686b9db7444ecdab1ee8d883d2c8fe2fcafcf53))

- **static**: Remove docs static files
  ([`1c573cc`](https://github.com/fossology/fossology-python/commit/1c573ccb8e9d2494be2cd21e57164b8ca24febd5))

- **update**: Version 0.0.10 compatible with API 1.0.12
  ([`e1d2334`](https://github.com/fossology/fossology-python/commit/e1d233428926073122af80d1adb2c8bb83fb6039))

- **update**: Version 0.0.10 compatible with API 1.0.12
  ([`50ce576`](https://github.com/fossology/fossology-python/commit/50ce576f9874f4cb3cb515db5362ed45491b2cd1))

- **workflows**: Only run when Python files changed
  ([`6bd0bb3`](https://github.com/fossology/fossology-python/commit/6bd0bb3d6688f1a04ccec2f9f6a7d79c12a42c22))

### Documentation

- **all**: Move build docs to gh-pages branch
  ([`2a12603`](https://github.com/fossology/fossology-python/commit/2a12603052bd38692ad3122f43497429fb78c0f6))

- **all**: Update static docs folder
  ([`38e9056`](https://github.com/fossology/fossology-python/commit/38e9056e4cdee7b2ea1a3b6cda5dc90834123cc9))

- **readme**: Add more badges
  ([`c14f016`](https://github.com/fossology/fossology-python/commit/c14f016bf5f55484e329b8c65f21119c3e805d9d))

- **sphinx**: Add/update code samples and default value
  ([`165da41`](https://github.com/fossology/fossology-python/commit/165da41d4c2bae00aab819e2401484b05c51d7cb))

### Features

- **0.0.9**: Fix minor bugs, update version
  ([`f782057`](https://github.com/fossology/fossology-python/commit/f7820574f25c913bbc78b67644e803060afc128b))

- **api**: Update to version 1.0.10
  ([`429bcc1`](https://github.com/fossology/fossology-python/commit/429bcc1faa62793004692b2564103b5a7b890689))

Add upload summary endpoint Use retry decorator in case of 503 Add a new test case

- **version**: New 0.0.11
  ([`f24ea05`](https://github.com/fossology/fossology-python/commit/f24ea054665eb42e6780d81e751806ae467642bd))


## v0.0.7 (2020-02-03)

### Bug Fixes

- **readme**: Correct rst notes
  ([`8ce3ad8`](https://github.com/fossology/fossology-python/commit/8ce3ad8852cdc6607494f908313a4c694f7606ce))

- **test**: Add some more sleep
  ([`3cdf358`](https://github.com/fossology/fossology-python/commit/3cdf358ae410ac483bb037ea28b9896b8cf751ee))

- **users**: Adopt minor changes in the API
  ([`86239cb`](https://github.com/fossology/fossology-python/commit/86239cb5b6a01b0b9ec4c63dc3da18ee8c8977f8))

- **users**: Normal users don't see everything
  ([`eb0022e`](https://github.com/fossology/fossology-python/commit/eb0022e0a3ac80dd568ab30890ba6bc41e68500a))

### Chores

- **ci**: Switch to python slim image
  ([`a98c12f`](https://github.com/fossology/fossology-python/commit/a98c12fb795cd0ef3ce23c68e1f455e8eacfe61f))

- **version**: Update minor version
  ([`d254871`](https://github.com/fossology/fossology-python/commit/d254871e192f773dbaa0269d17f2af33d354b873))

- **version**: Update release number
  ([`f581104`](https://github.com/fossology/fossology-python/commit/f58110416e363ef87b11757cb226bd4f85a1456b))

### Documentation

- **jobs**: Add example for job specification
  ([`88456b7`](https://github.com/fossology/fossology-python/commit/88456b762087acf361b507c8c927be5bf9a3b0a1))

- **readme**: Add more details
  ([`2a8a7c9`](https://github.com/fossology/fossology-python/commit/2a8a7c92110f2c21051fa0b910acecdd345a6396))

### Refactoring

- **tests**: Move tests folder to root
  ([`cf16562`](https://github.com/fossology/fossology-python/commit/cf1656227b3eba658de616975c9c6893fecb93a6))


## v0.0.5 (2019-12-11)

### Bug Fixes

- Inform ghp it's not a jekyll site
  ([`e78c3d7`](https://github.com/fossology/fossology-python/commit/e78c3d71d7e1f9c5edcb2dcb32454a006e3061d0))

- Links in README, add badges
  ([`f272620`](https://github.com/fossology/fossology-python/commit/f272620c778d499e247d9f94919950d14782177f))

- Use correct body type for jobs
  ([`c400e8b`](https://github.com/fossology/fossology-python/commit/c400e8bba863416193c55dec3a5de03cf76d079e))

- **api**: Format
  ([`992dd5f`](https://github.com/fossology/fossology-python/commit/992dd5f2356748e374bd42a2e68ab1add06a2306))

- **spdx**: Update license identifier
  ([`0403aed`](https://github.com/fossology/fossology-python/commit/0403aed3523002a0e88264f309de2292deb977b8))

### Chores

- Create two distinct workflow, use services
  ([`1776fe8`](https://github.com/fossology/fossology-python/commit/1776fe854d208a26d9abd37bad34efde4fc25dbd))

- Update path for tests
  ([`fd284d4`](https://github.com/fossology/fossology-python/commit/fd284d4afc37de27b2d0e931f61d2af587058a0b))

- Update python dependencies
  ([`eacc383`](https://github.com/fossology/fossology-python/commit/eacc383e70d441c3bcab6365ee93ac75d0b1d315))

- Use environment variables in CI
  ([`e6720bf`](https://github.com/fossology/fossology-python/commit/e6720bf76d9cfa6978113aea2c1449a879ae22c8))

- Use poetry to manage python env for tests
  ([`ce5a0fe`](https://github.com/fossology/fossology-python/commit/ce5a0feb737cc818d3fe73a68fb2a0d01c7481ae))

- **ci**: Only install dev dependencies
  ([`314261d`](https://github.com/fossology/fossology-python/commit/314261d612c3e1cd893f92901fbb74fa39c3f3e6))

- **ci**: Remove proxy settings
  ([`1463029`](https://github.com/fossology/fossology-python/commit/14630296fc4c435dea24c09994372d4fc5c31412))

- **pip**: Update deps, add deploy cmd
  ([`aca67a5`](https://github.com/fossology/fossology-python/commit/aca67a575023f04d5d718bc1a5f612e1a9385c84))

- **pip**: Update lock
  ([`9e305fa`](https://github.com/fossology/fossology-python/commit/9e305fae26392f21a242e2c4f4fa126147dc8439))

- **poetry**: Replace pipenv by poetry
  ([`0833b1c`](https://github.com/fossology/fossology-python/commit/0833b1c87d68be1c359f6d3426f557723888e38c))

### Documentation

- Update project readme
  ([`7d3105d`](https://github.com/fossology/fossology-python/commit/7d3105d68ed750b22c6a2ce3880296b6a05b10ba))

- **all**: Update docs to new classes
  ([`8812675`](https://github.com/fossology/fossology-python/commit/8812675612df5787adeebfe7d5a7b4bac70c6b5d))

- **all**: Update documentation
  ([`236f527`](https://github.com/fossology/fossology-python/commit/236f5273d985399480e9605fbbef2f33a5eb3f27))

- **link**: Update docs deployment path
  ([`89c12d4`](https://github.com/fossology/fossology-python/commit/89c12d440269414214144789e6fd331dc86a8628))

- **url**: Update download url
  ([`47fdc80`](https://github.com/fossology/fossology-python/commit/47fdc80ca293f193da8c7fabb989cb0696b8a52a))

### Features

- Add upload from vcs
  ([`9718834`](https://github.com/fossology/fossology-python/commit/9718834c0959c2fde51631948b5148c98f8b8cc2))

- Create basic project workflow
  ([`005620f`](https://github.com/fossology/fossology-python/commit/005620f884f87fd7ea5708dfad52f7d4b06ffb9c))

- Create docs build directory to be exported as pages
  ([`b5ee842`](https://github.com/fossology/fossology-python/commit/b5ee842138bec4c96c53e1a638d6953faddd77d7))

- Create testsuite to run all tests in the right order
  ([`0bc6e77`](https://github.com/fossology/fossology-python/commit/0bc6e7719938439a48e7c59579725a1b2e2b5e8d))

- First official release
  ([`b869006`](https://github.com/fossology/fossology-python/commit/b8690069750aaa5303158b716165ca8c232bbd91))

- Import initial code from Siemens internal repository
  ([`7013126`](https://github.com/fossology/fossology-python/commit/7013126e39d3a7dc0be1bb2fab880920983049df))

- Really add the compiled docs
  ([`cad9380`](https://github.com/fossology/fossology-python/commit/cad93803207043bbfcfc6b0aadb16c914ddc41ff))

- **0.0.4**: Update to API v1.0.6
  ([`669aee6`](https://github.com/fossology/fossology-python/commit/669aee6155bf8580708f61880d0007e96421b448))

- **api**: Continue working on the initla version
  ([`741c489`](https://github.com/fossology/fossology-python/commit/741c4891e72f15c9b603eea197ab047a88bfc57f))

- **api**: Extend API coverage
  ([`eef9759`](https://github.com/fossology/fossology-python/commit/eef97590dd2ccb1a23f31763a458444046d927a7))

- **api**: Small api improvements
  ([`4de26aa`](https://github.com/fossology/fossology-python/commit/4de26aad1ae0d5738726a0a70bae75db5013fd59))

- **api**: Update to api version 1.0.3
  ([`d726201`](https://github.com/fossology/fossology-python/commit/d726201072f4477a06123ab1554119d7ba9f3a13))

improve exception handling add new endpoints and object (uploads, jobs) improve test

- **init**: Initial project import
  ([`5f0957d`](https://github.com/fossology/fossology-python/commit/5f0957dc56589289efd87593e262c9f2293f241d))

- **upload**: Add basic endpoints for uploads
  ([`0f58f7a`](https://github.com/fossology/fossology-python/commit/0f58f7ad36681e9e02169cba14a1524cd1fc47f0))

### Refactoring

- Use individual tests
  ([`4801cad`](https://github.com/fossology/fossology-python/commit/4801cad77d4ecd38b368ea6e6760df621577d00c))

- **classes**: Use class inheritance for more readability
  ([`4af664d`](https://github.com/fossology/fossology-python/commit/4af664d1ee0a675cf29b525444d2f4d80c9a17d6))

Use permissive MIT license, remove information about the author add Siemens AG as copyright owner,
  rename lib to fossology, increase version
