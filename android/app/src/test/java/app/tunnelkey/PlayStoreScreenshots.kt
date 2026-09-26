package app.tunnelkey

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.test.hasContentDescription
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performTextInput
import androidx.test.ext.junit.runners.AndroidJUnit4
import app.tunnelkey.data.CodePosition
import app.tunnelkey.data.Profile
import app.tunnelkey.managed.ManagedConfig
import app.tunnelkey.managed.ManagedLink
import app.tunnelkey.managed.TotpParams
import app.tunnelkey.provision.SetupLink
import app.tunnelkey.provision.SetupPayload
import app.tunnelkey.provision.SetupTotp
import app.tunnelkey.security.PinResult
import app.tunnelkey.ui.EditorForm
import app.tunnelkey.ui.SignInRequest
import app.tunnelkey.ui.screens.EditorScreen
import app.tunnelkey.ui.screens.HomeScreen
import app.tunnelkey.ui.screens.LockScreen
import app.tunnelkey.ui.screens.LockSetupScreen
import app.tunnelkey.ui.screens.ManagedHomeScreen
import app.tunnelkey.ui.screens.SignInSheet
import app.tunnelkey.ui.theme.TunnelkeyTheme
import app.tunnelkey.vpn.Phase
import app.tunnelkey.vpn.TunnelStatus
import com.github.takahirom.roborazzi.captureRoboImage
import com.github.takahirom.roborazzi.captureScreenRoboImage
import org.junit.Assume.assumeTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

/**
 * Renders the Google Play screenshots from the real screens with demo data.
 * Only runs with:  ./gradlew :app:testDebugUnitTest -PplayScreenshots --tests '*PlayStoreScreenshots*'
 * Output: docs/play-store/screens-raw/  (framed by docs/play-store/make_graphics.py)
 */
@RunWith(AndroidJUnit4::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [35], qualifiers = "w360dp-h720dp-xxhdpi")
class PlayStoreScreenshots {

    @get:Rule val compose = createComposeRule()

    private val dir get() = System.getProperty("screenshotDir")!!

    @Before fun onlyWhenRequested() = assumeTrue(System.getProperty("playScreenshots") == "true")

    private fun screen(content: @Composable () -> Unit) = compose.setContent {
        TunnelkeyTheme(dark = true) {
            Surface(Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) { content() }
        }
    }

    private val now = System.currentTimeMillis()

    private val officeConfig = ManagedConfig(
        name = "Office VPN",
        profileId = "office",
        username = "j.novak",
        hasPassword = true,
        totp = TotpParams(6, 30, "SHA1"),
        links = listOf(
            ManagedLink("Intranet", "web", "https://intranet.example.com"),
            ManagedLink("My office PC", "rdp", "rdp://full%20address=s:10.20.0.25:3389&username=s:CORP%5Cj.novak"),
            ManagedLink("Helpdesk", "web", "https://helpdesk.example.com/tickets"),
        ),
    )

    private val profiles = listOf(
        Profile("office", "Office VPN", "vpn.example.com:1194/udp", "j.novak", twoFactor = true),
        Profile("lab", "Lab network", "lab.example.org:443/tcp", "jnovak"),
        Profile("home", "Home server", "home.example.net:1194/udp", needsCredentials = false),
    )

    @Test fun s1_connected() {
        screen {
            ManagedHomeScreen(
                config = officeConfig,
                status = TunnelStatus(
                    phase = Phase.Connected, profileId = "office", connectedAt = now - (83 * 60 + 12) * 1000L,
                    bytesIn = 482_300_000, bytesOut = 36_900_000, vpnAddress = "10.8.0.14",
                    server = "vpn.example.com:1194/udp",
                ),
                hint = null, onConnect = {}, onDisconnect = {}, onOpenLink = {}, onOpenLogs = {},
                onSecurity = {}, onAbout = {}, onRemove = {},
            )
        }
        compose.onRoot().captureRoboImage("$dir/1_connected.png")
    }

    @Test fun s2_signIn() {
        val profile = profiles[0]
        screen {
            HomeScreen(
                profiles = profiles, selected = profile, status = TunnelStatus(),
                onSelect = {}, onEdit = {}, onImport = {}, onScan = {}, onConnect = {}, onDisconnect = {},
                onOpenLogs = {}, onAbout = {},
            )
            SignInSheet(
                request = SignInRequest(profile, needsPassword = false, needsCode = true, usesStaticChallenge = false),
                onSubmit = { _, _ -> }, onDismiss = {},
            )
        }
        compose.onNode(hasContentDescription("Authenticator code")).performTextInput("4829")
        compose.waitForIdle()
        captureScreenRoboImage("$dir/2_sign_in.png")
    }

    @Test fun s3_profiles() {
        screen {
            HomeScreen(
                profiles = profiles, selected = profiles[0], status = TunnelStatus(),
                onSelect = {}, onEdit = {}, onImport = {}, onScan = {}, onConnect = {}, onDisconnect = {},
                onOpenLogs = {}, onAbout = {},
            )
        }
        compose.onRoot().captureRoboImage("$dir/3_profiles.png")
    }

    @Test fun s4_editor() {
        screen {
            EditorScreen(
                form = EditorForm(
                    id = "office", name = "Office VPN", remote = "vpn.example.com:1194/udp", username = "j.novak",
                    twoFactor = true, codePosition = CodePosition.AFTER_PASSWORD, codeLength = 6,
                    rememberPassword = true, hasSavedPassword = true,
                ),
                onChange = {}, onSave = {}, onDelete = {}, onBack = {},
            )
        }
        compose.onRoot().captureRoboImage("$dir/4_two_factor.png")
    }

    @Test fun s5_setupCode() {
        screen {
            LockSetupScreen(
                payload = SetupPayload(
                    version = 1, name = "Office VPN", ovpn = "client", username = "j.novak", password = "x",
                    totp = SetupTotp("JBSWY3DPEHPK3PXP"),
                    links = listOf(SetupLink("Intranet", "web", "https://x"), SetupLink("PC", "rdp", "rdp://x"), SetupLink("Helpdesk", "web", "https://y")),
                ),
                biometricAvailable = true, replacesExisting = false,
                onBiometric = {}, onPin = {}, onNoLock = {}, onBack = {},
            )
        }
        compose.onRoot().captureRoboImage("$dir/5_setup_code.png")
    }

    @Test fun s6_locked() {
        screen {
            LockScreen(
                name = "Office VPN", usesPin = true, onBiometric = {},
                onPin = { PinResult.Wrong(9, 0) }, lockedUntil = 0, message = null,
            )
        }
        for (d in listOf("3", "9", "1", "7", "4")) compose.onNode(hasText(d)).performClick()
        compose.waitForIdle()
        compose.onRoot().captureRoboImage("$dir/6_locked.png")
    }
}
