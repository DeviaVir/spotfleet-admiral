dockerBuild {
    name = 'deviavir/spotfleet-admiral'
    testCommand = 'make composetest'
    reports = [
        tests: '**/build/nosetests.xml',
        tasks: '**/*.py'
    ]
}
