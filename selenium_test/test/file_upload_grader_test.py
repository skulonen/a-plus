import unittest

from test_initializer import TestInitializer
from selenium_test.page_objects.page_objects import CourseName, LoginPage, FileUploadGrader


class FileUploadGraderTest(unittest.TestCase):
    def setUp(self):
        testInitializer = TestInitializer()
        self.driver = testInitializer.getFirefoxDriverWithLoggingEnabled()
        testInitializer.recreateDatabase()
        LoginPage(self.driver).loginToCourse(CourseName.APLUS)

    def testShouldGiveZeroPointsOnEmptySubmit(self):
        fileUploadPage = FileUploadGrader(self.driver)
        fileUploadPage.submit()

        self.assertEqual(fileUploadPage.getAllowedSubmissions(), '1/10')
        self.assertEqual(fileUploadPage.getExerciseScore(), '0 / 100')
        self.assertEqual(fileUploadPage.getNumberOfSubmitters(), '1')
        self.assertEqual(fileUploadPage.getAverageSubmissionsPerStudent(), '1.00')

    def tearDown(self):
        self.driver.close()

if __name__ == '__main__':
    unittest.main(verbosity=2, warnings='ignore')
