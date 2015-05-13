import unittest

from test_initializer import TestInitializer
from selenium_test.page_objects.page_objects import CourseName, LoginPage, HomePage


class LoginTest(unittest.TestCase):
    logoutPageURI = '/accounts/logout'

    def setUp(self):
       self.driver = TestInitializer().getFirefoxDriverWithLoggingEnabled()

    def testLoginToTestCourseInstance(self):
        LoginPage(self.driver).loginToCourse(CourseName.APLUS)
        homePage = HomePage(self.driver, CourseName.APLUS)
        self.assertEqual(homePage.getCourseBanner(), 'A+ Test Course Instance')
        self.assertTrue(LoginPage.defaultUsername in homePage.getLoggedInText())

    def testLoginToExampleHookCourseInstance(self):
        LoginPage(self.driver).loginToCourse(CourseName.HOOK)
        homePage = HomePage(self.driver, CourseName.HOOK)
        self.assertEqual(homePage.getCourseBanner(), 'Hook Example')
        self.assertTrue(LoginPage.defaultUsername in homePage.getLoggedInText())

    def testShouldThrowTimoutExceptionOnWrongCredentials(self):
        loginPage = LoginPage(self.driver)
        try:
            loginPage.loginToCourse(CourseName.APLUS, 'fake', 'password')
        except Exception:
            return

        self.fail("There should have been an exception")

    def tearDown(self):
        self.driver.close()

if __name__ == '__main__':
    unittest.main(verbosity=2, warnings='ignore')
