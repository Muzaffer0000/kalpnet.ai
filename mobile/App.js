import { useEffect, useRef, useState } from "react";
import {
  AccessibilityInfo, Animated, Easing, Linking, Platform, Pressable, ScrollView,
  StatusBar, StyleSheet, Text, TextInput, View,
} from "react-native";
import { StatusBar as ExpoStatusBar } from "expo-status-bar";
import model from "./src/model.json";
import { score, isUrgent } from "./src/score.js";
import { Q, PAIN } from "./src/questions.js";
import { readInput } from "./src/validate.js";

const C = { fg: "#1a1a1a", mut: "#555", card: "#f4f4f6", bd: "#8a8a94", red: "#b00020", blue: "#0b57d0", bg: "#fff" };
const STEPS = [["Nefes alın", 4, 1.4], ["Tutun", 4, 1.4], ["Yavaşça verin", 6, 1]];
const call112 = () => Linking.openURL("tel:112");

function Btn({ label, onPress, style, textStyle, ...rest }) {
  return (
    <Pressable accessibilityRole="button" accessibilityLabel={label} onPress={onPress} style={[s.btn, style]} {...rest}>
      <Text style={[s.btnText, textStyle]}>{label}</Text>
    </Pressable>
  );
}

const Call = () => <Btn label="112'yi ara" onPress={call112} style={{ backgroundColor: C.red }} />;

// Seçenek düğmesi (radyo): seçili değilse çerçeveli, seçiliyse dolu.
function Choice({ label, a11y, on, onPress }) {
  return (
    <Pressable accessibilityRole="radio" accessibilityLabel={a11y || label} accessibilityState={{ checked: on }}
      onPress={onPress} style={[s.choice, on && s.choiceOn]}>
      <Text style={[s.choiceText, on && s.choiceTextOn]}>{label}</Text>
    </Pressable>
  );
}

function Breathing() {
  const [running, setRunning] = useState(false);
  const [phase, setPhase] = useState("Hazır");
  const scale = useRef(new Animated.Value(1)).current;
  const reduce = useRef(false);
  const timer = useRef(null);

  useEffect(() => {
    AccessibilityInfo.isReduceMotionEnabled().then(v => { reduce.current = v; }).catch(() => {});
  }, []);

  const stop = () => {
    clearTimeout(timer.current); timer.current = null;
    scale.stopAnimation(); scale.setValue(1);
    setRunning(false); setPhase("Hazır");
  };
  useEffect(() => () => { clearTimeout(timer.current); scale.stopAnimation(); }, [scale]);

  const start = () => {
    setRunning(true);
    let i = 0;
    const next = () => {
      const [t, sec, sc] = STEPS[i++ % 3];
      setPhase(t);
      if (!reduce.current) Animated.timing(scale, { toValue: sc, duration: sec * 1000, easing: Easing.linear, useNativeDriver: true }).start();
      timer.current = setTimeout(next, sec * 1000);
    };
    next();
  };

  return (
    <View style={s.card}>
      <Text accessibilityRole="header" style={s.h2}>Nefes egzersizi (4-4-6)</Text>
      <Text style={s.small}>Burnunuzdan 4 sn nefes alın, 4 sn tutun, 6 sn ağzınızdan verin. Bu, panik hissini yatıştırmaya yardım edebilir; belirtileriniz sürerse acile gidin.</Text>
      <View style={s.circleBox} importantForAccessibility="no-hide-descendants" accessibilityElementsHidden>
        <Animated.View style={[s.circle, { transform: [{ scale }] }]}>
          <Text style={s.circleText}>{phase}</Text>
        </Animated.View>
      </View>
      <Text style={[s.small, { textAlign: "center" }]} accessibilityLiveRegion="polite">{running ? phase : ""}</Text>
      <Btn label={running ? "Durdur" : "Başlat"} onPress={running ? stop : start}
        style={s.secBtn} textStyle={{ color: C.blue }} />
    </View>
  );
}

export default function App() {
  const [age, setAge] = useState("");
  const [dur, setDur] = useState("");
  const [pain, setPain] = useState("");
  const [answers, setAnswers] = useState({});
  const [error, setError] = useState("");
  const [p, setP] = useState(null);
  const [resultKey, setResultKey] = useState(0);
  const scroller = useRef(null);
  const pendingScroll = useRef(false);

  const keys = Object.keys(model.binary);
  const broken = keys.some(k => !(k in Q));

  const submit = () => {
    const x = readInput(model, { age, dur, pain, answers });
    if (typeof x === "string") { setError(x); AccessibilityInfo.announceForAccessibility(x); return; }
    setError("");
    const pr = score(model, x);
    setP(pr);
    pendingScroll.current = true;
    setResultKey(k => k + 1); // sonuç kartı ve nefes egzersizi yeniden oluşsun
    // iOS accessibilityLiveRegion'ı yok sayar; PWA'daki r.focus() yerine duyur.
    AccessibilityInfo.announceForAccessibility(isUrgent(model, pr)
      ? "Acil kalp kaynaklı olabilir — hemen 112'yi arayın / acile gidin"
      : "Bu araca göre risk daha düşük görünüyor");
  };

  const urgent = p !== null && isUrgent(model, p);

  return (
    <View style={s.root}>
      <ExpoStatusBar style="dark" />
      <ScrollView ref={scroller} contentContainerStyle={s.content} keyboardShouldPersistTaps="handled">
        <Text accessibilityRole="header" style={s.h1}>Göğüs Ağrısı Ön Değerlendirme</Text>

        <View style={[s.card, s.alert]}>
          <Text accessibilityRole="header" style={[s.h2, { color: C.red }]}>Önce bunu okuyun: acil belirtiler</Text>
          <Text style={s.body}>Aşağıdakilerden biri varsa <Text style={s.bold}>formu doldurmayın, hemen 112'yi arayın</Text>:</Text>
          {[
            "Göğsünüzü ezen/sıkıştıran bir ağrı ve 15 dakikadan uzun sürüyor",
            "Ağrı kola, çeneye veya sırta yayılıyor",
            "Soğuk terleme, bayılma ya da bayılacak gibi olma",
            "Şiddetli nefes darlığı",
          ].map(t => <Text key={t} style={s.li}>{"•  "}{t}</Text>)}
          <Call />
        </View>

        <View style={s.card}>
          <Text accessibilityRole="header" style={s.h2}>Sorular</Text>
          {broken ? (
            <Text style={s.body}>Model yüklenemedi. Acil belirtiniz varsa 112'yi arayın.</Text>
          ) : (
            <>
              <Text style={s.label}>Yaşınız</Text>
              <TextInput style={s.input} value={age} onChangeText={setAge} keyboardType="number-pad"
                maxLength={3} accessibilityLabel="Yaşınız" />
              <Text style={s.label}>Ağrının türü</Text>
              <View accessibilityRole="radiogroup" accessibilityLabel="Ağrının türü">
                {model.categorical.categories.map(c => (
                  <Choice key={c} label={PAIN[c] || c} on={pain === c} onPress={() => setPain(c)} />
                ))}
              </View>
              <Text style={s.label}>Ağrı kaç dakikadır sürüyor?</Text>
              <TextInput style={s.input} value={dur} onChangeText={setDur} keyboardType="number-pad"
                maxLength={5} accessibilityLabel="Ağrı kaç dakikadır sürüyor?" />
              <Text style={s.small}>Saat ise dakikaya çevirin (1 saat = 60). Tüm soruları cevaplayın.</Text>
              {keys.map(k => (
                <View key={k} style={s.q} accessibilityRole="radiogroup">
                  <Text style={s.label}>{Q[k]}</Text>
                  <View style={s.yn}>
                    <Choice label="Evet" a11y={`${Q[k]} Evet`} on={answers[k] === "1"} onPress={() => setAnswers(a => ({ ...a, [k]: "1" }))} />
                    <Choice label="Hayır" a11y={`${Q[k]} Hayır`} on={answers[k] === "0"} onPress={() => setAnswers(a => ({ ...a, [k]: "0" }))} />
                  </View>
                </View>
              ))}
              {error ? <Text style={s.err} accessibilityRole="alert" accessibilityLiveRegion="polite">{error}</Text> : null}
              <Btn label="Değerlendir" onPress={submit} style={{ marginTop: 12 }} />
            </>
          )}
        </View>

        {p !== null && (
          <>
            <View key={resultKey} style={[s.card, urgent && s.alert]}
              onLayout={e => {
                if (!pendingScroll.current) return;
                pendingScroll.current = false;
                scroller.current?.scrollTo({ y: e.nativeEvent.layout.y, animated: true });
              }}
              accessibilityLiveRegion="polite">
              {urgent ? (
                <>
                  <Text accessibilityRole="header" style={[s.h2, { color: C.red }]}>Acil kalp kaynaklı olabilir — hemen 112'yi arayın / acile gidin</Text>
                  <Text style={s.body}>Bu araç, verdiğiniz bilgilere göre kalp kaynaklı acil bir durumu dışlayamıyor. Beklemeyin.</Text>
                </>
              ) : (
                <>
                  <Text accessibilityRole="header" style={s.h2}>Bu araca göre risk daha düşük görünüyor</Text>
                  <Text style={s.body}>Ancak bu araç kalp krizini <Text style={s.bold}>dışlayamaz</Text>. Şüpheniz varsa, belirtileriniz sürüyorsa ya da kötüleşiyorsa vakit kaybetmeden acile gidin veya 112'yi arayın.</Text>
                </>
              )}
              <Call />
            </View>
            {!urgent && <Breathing key={`b${resultKey}`} />}
          </>
        )}
      </ScrollView>
      <View style={s.footer}>
        <Text style={s.footerText}>Tıbbi cihaz değildir, tanı koymaz. Sentetik veriyle eğitilmiş bir prototiptir. Verileriniz cihazınızdan çıkmaz.</Text>
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: C.bg, paddingTop: Platform.OS === "android" ? StatusBar.currentHeight || 0 : 44 },
  content: { padding: 16, paddingBottom: 24 },
  h1: { fontSize: 22, fontWeight: "700", color: C.fg, marginVertical: 4 },
  h2: { fontSize: 18, fontWeight: "700", color: C.fg, marginBottom: 8 },
  card: { backgroundColor: C.card, borderRadius: 12, padding: 14, marginVertical: 8 },
  alert: { borderWidth: 3, borderColor: C.red },
  body: { fontSize: 17, lineHeight: 25, color: C.fg, marginBottom: 8 },
  bold: { fontWeight: "700" },
  li: { fontSize: 17, lineHeight: 25, color: C.fg, marginBottom: 4, paddingLeft: 8 },
  small: { fontSize: 14, color: C.mut, marginVertical: 6 },
  label: { fontSize: 17, fontWeight: "600", color: C.fg, marginTop: 10, marginBottom: 4 },
  input: { minHeight: 48, fontSize: 18, padding: 8, borderWidth: 2, borderColor: C.bd, borderRadius: 8, backgroundColor: C.bg, color: C.fg },
  btn: { minHeight: 52, padding: 12, borderRadius: 10, backgroundColor: C.blue, alignItems: "center", justifyContent: "center", marginTop: 8 },
  btnText: { color: "#fff", fontSize: 18, fontWeight: "700" },
  secBtn: { backgroundColor: "transparent", borderWidth: 2, borderColor: C.blue },
  choice: { flex: 1, minHeight: 48, justifyContent: "center", alignItems: "center", borderWidth: 2, borderColor: C.bd, borderRadius: 8, marginVertical: 3, paddingHorizontal: 8 },
  choiceOn: { backgroundColor: C.blue, borderColor: C.blue },
  choiceText: { fontSize: 17, color: C.fg, textAlign: "center" },
  choiceTextOn: { color: "#fff", fontWeight: "700" },
  q: { paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: C.bd },
  yn: { flexDirection: "row", gap: 8 },
  err: { color: C.red, fontWeight: "700", fontSize: 17, marginTop: 12 },
  circleBox: { height: 180, alignItems: "center", justifyContent: "center" },
  circle: { width: 120, height: 120, borderRadius: 60, backgroundColor: C.blue, alignItems: "center", justifyContent: "center" },
  circleText: { color: "#fff", fontWeight: "700", fontSize: 18 },
  footer: { borderTopWidth: 2, borderTopColor: C.red, backgroundColor: C.bg, paddingVertical: 8, paddingHorizontal: 16 },
  footerText: { fontSize: 13, color: C.fg },
});
