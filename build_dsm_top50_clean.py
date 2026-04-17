import json
import re
from pathlib import Path

from pypdf import PdfReader


PDF_PATH = Path(r"C:\Users\Dell\OneDrive\Desktop\MindLex AI\DSM-5.pdf")
OUTPUT_PATH = Path(r"C:\Users\Dell\OneDrive\Desktop\MindLex AI\dsm_top50_clean.json")


def snake_case(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    slug = re.sub(r"_+", "_", slug)
    return slug or "symptom"


def unique_strings(values):
    seen = set()
    result = []
    for value in values:
        cleaned = re.sub(r"\s+", " ", value.strip())
        if cleaned and cleaned.lower() not in seen:
            seen.add(cleaned.lower())
            result.append(cleaned)
    return result


def symptom_objects(symptoms):
    items = []
    used_ids = set()
    for text in unique_strings(symptoms):
        base = snake_case(text)
        candidate = base
        counter = 2
        while candidate in used_ids:
            candidate = f"{base}_{counter}"
            counter += 1
        used_ids.add(candidate)
        items.append({"id": candidate, "text": text})
    return items


def keywords(values):
    return unique_strings(values)


def disorder(category, name, code, criteria_a, criteria_b, criteria_c, symptoms, duration, tags, risk_level):
    return {
        "category": category,
        "name": name,
        "code": code,
        "criteria": {
            "A": criteria_a,
            "B": criteria_b,
            "C": criteria_c,
        },
        "symptoms": symptom_objects(symptoms),
        "duration": duration,
        "severity": ["mild", "moderate", "severe"],
        "keywords": keywords(tags),
        "risk_level": risk_level,
    }


DATA = [
    disorder(
        "Neurodevelopmental Disorders",
        "Autism Spectrum Disorder",
        "F84.0",
        "Persistent deficits in social communication and social interaction across settings.",
        "Restricted, repetitive patterns of behavior, interests, or sensory responses are present.",
        "Symptoms begin early in development, impair daily functioning, and are not better explained by intellectual disability alone.",
        [
            "limited back-and-forth conversation",
            "reduced eye contact or nonverbal communication",
            "difficulty making or keeping relationships",
            "repetitive movements or speech",
            "strong need for routines",
            "highly fixed interests",
            "sensory overreaction or underreaction",
        ],
        "Starts in early developmental period",
        ["autism", "asd", "social communication problems", "repetitive behaviors", "sensory issues", "rigid routines"],
        "medium",
    ),
    disorder(
        "Neurodevelopmental Disorders",
        "Attention-Deficit/Hyperactivity Disorder",
        "F90.2",
        "A persistent pattern of inattention and/or hyperactivity-impulsivity interferes with functioning or development.",
        "Several symptoms are present before age 12 and occur in two or more settings such as home, school, or work.",
        "Symptoms cause clear impairment and are not better explained by another mental disorder.",
        [
            "difficulty sustaining attention",
            "careless mistakes",
            "seems not to listen",
            "does not finish tasks",
            "loses things easily",
            "fidgeting",
            "excessive talking",
            "interrupting others",
        ],
        "Chronic pattern with onset before age 12",
        ["adhd", "attention problems", "hyperactivity", "impulsivity", "distractible", "restless"],
        "medium",
    ),
    disorder(
        "Neurodevelopmental Disorders",
        "Language Disorder",
        "F80.2",
        "Persistent difficulties in learning and using language across speaking, writing, sign language, or understanding.",
        "Language ability is clearly below what is expected for age and causes functional limits in communication, school, or work.",
        "Symptoms begin in development and are not better explained by hearing loss, intellectual disability, or another condition.",
        [
            "limited vocabulary",
            "short or simple sentences",
            "grammar mistakes",
            "difficulty understanding spoken language",
            "difficulty telling stories or explaining ideas",
        ],
        "Begins in early development",
        ["language disorder", "speech and language delay", "trouble understanding words", "expressive language problems", "communication delay"],
        "low",
    ),
    disorder(
        "Neurodevelopmental Disorders",
        "Developmental Coordination Disorder",
        "F82",
        "Learning and execution of coordinated motor skills are substantially below age expectations.",
        "Motor problems interfere with self-care, school tasks, play, or productivity.",
        "Symptoms begin early in development and are not due to intellectual disability, visual impairment, or a neurological disease.",
        [
            "clumsy movements",
            "poor balance",
            "drops or bumps into things",
            "slow handwriting or fine motor work",
            "difficulty learning sports or coordinated tasks",
        ],
        "Begins in early developmental period",
        ["coordination disorder", "clumsy child", "motor skill problems", "fine motor difficulty", "poor balance"],
        "low",
    ),
    disorder(
        "Neurodevelopmental Disorders",
        "Tourette's Disorder",
        "F95.2",
        "Multiple motor tics and at least one vocal tic have been present at some point, though not always at the same time.",
        "Tics wax and wane but persist for more than 1 year since first tic onset.",
        "Onset occurs before age 18 and symptoms are not due to a substance or another medical condition.",
        [
            "eye blinking",
            "facial grimacing",
            "shoulder shrugging",
            "throat clearing",
            "sniffing sounds",
            "sudden repetitive vocalizations",
        ],
        "More than 1 year",
        ["tourette", "tics", "motor tics", "vocal tics", "throat clearing", "blinking"],
        "low",
    ),
    disorder(
        "Schizophrenia Spectrum and Other Psychotic Disorders",
        "Delusional Disorder",
        "F22",
        "One or more delusions are present for at least 1 month.",
        "Schizophrenia criteria have never been fully met, and functioning outside the delusion is not markedly odd.",
        "Mood episodes are brief compared with the delusional periods, and symptoms are not due to substances or medical illness.",
        [
            "fixed false beliefs",
            "persecutory ideas",
            "jealous beliefs",
            "grandiose beliefs",
            "somatic delusions",
        ],
        "At least 1 month",
        ["delusional disorder", "fixed false belief", "paranoia", "persecutory beliefs", "unshakeable belief"],
        "high",
    ),
    disorder(
        "Schizophrenia Spectrum and Other Psychotic Disorders",
        "Brief Psychotic Disorder",
        "F23",
        "Sudden onset of one or more psychotic symptoms such as delusions, hallucinations, disorganized speech, or grossly disorganized behavior.",
        "At least one symptom is delusions, hallucinations, or disorganized speech.",
        "Episode lasts at least 1 day but less than 1 month, with eventual full return to previous functioning, and is not better explained by mood disorder or substances.",
        [
            "delusions",
            "hallucinations",
            "disorganized speech",
            "grossly disorganized behavior",
            "rapid change from baseline",
        ],
        "1 day to less than 1 month",
        ["brief psychosis", "sudden psychosis", "hallucinations", "delusions", "disorganized behavior"],
        "high",
    ),
    disorder(
        "Schizophrenia Spectrum and Other Psychotic Disorders",
        "Schizophreniform Disorder",
        "F20.81",
        "Two or more core psychotic symptoms are present, with at least one being delusions, hallucinations, or disorganized speech.",
        "Symptoms last long enough to meet the syndrome but the total duration is less than 6 months.",
        "Mood and medical causes do not better explain the presentation.",
        [
            "delusions",
            "hallucinations",
            "disorganized speech",
            "disorganized or catatonic behavior",
            "reduced emotional expression",
            "social withdrawal",
        ],
        "1 month to less than 6 months",
        ["schizophreniform", "psychosis", "hallucinations", "delusions", "disorganized speech"],
        "high",
    ),
    disorder(
        "Schizophrenia Spectrum and Other Psychotic Disorders",
        "Schizophrenia",
        "F20.9",
        "Two or more core psychotic symptoms are present for a significant portion of time, and at least one is delusions, hallucinations, or disorganized speech.",
        "Functioning in work, relationships, or self-care is markedly worse than before the illness.",
        "Continuous signs of disturbance persist for at least 6 months and are not better explained by mood disorder, substances, or medical illness.",
        [
            "delusions",
            "hallucinations",
            "disorganized speech",
            "grossly disorganized behavior",
            "negative symptoms",
            "social withdrawal",
            "impaired reality testing",
        ],
        "At least 6 months",
        ["schizophrenia", "psychosis", "hearing voices", "delusions", "disorganized thinking", "negative symptoms"],
        "high",
    ),
    disorder(
        "Schizophrenia Spectrum and Other Psychotic Disorders",
        "Schizoaffective Disorder",
        "F25.1",
        "An uninterrupted illness includes a major mood episode together with core schizophrenia symptoms.",
        "There is a period of at least 2 weeks of delusions or hallucinations without a major mood episode.",
        "Mood symptoms are present for most of the total illness duration, and the condition is not due to substances or medical illness.",
        [
            "delusions",
            "hallucinations",
            "disorganized thinking",
            "major depression symptoms",
            "manic or hypomanic symptoms",
            "impaired functioning",
        ],
        "Ongoing illness with at least 2 weeks of psychosis without mood episode",
        ["schizoaffective", "psychosis with mood symptoms", "hallucinations", "delusions", "mania and psychosis", "depression and psychosis"],
        "high",
    ),
    disorder(
        "Bipolar and Related Disorders",
        "Bipolar I Disorder",
        "F31.9",
        "At least one manic episode has occurred, marked by abnormally elevated or irritable mood and increased energy.",
        "During the manic episode, symptoms such as decreased need for sleep, grandiosity, racing thoughts, pressured speech, or risky behavior are clearly present.",
        "Mood disturbance causes major impairment, may include psychosis or hospitalization, and is not due to substances or medical illness.",
        [
            "elevated or irritable mood",
            "increased energy",
            "decreased need for sleep",
            "grandiosity",
            "racing thoughts",
            "pressured speech",
            "risky behavior",
        ],
        "Mania lasts at least 1 week or any duration if hospitalized",
        ["bipolar 1", "mania", "high energy", "no sleep", "risky behavior", "mood swings"],
        "high",
    ),
    disorder(
        "Bipolar and Related Disorders",
        "Bipolar II Disorder",
        "F31.81",
        "There has been at least one hypomanic episode and at least one major depressive episode.",
        "There has never been a full manic episode.",
        "Mood episodes cause clinically significant distress or impairment and are not better explained by psychotic disorders.",
        [
            "periods of high energy",
            "reduced need for sleep",
            "increased confidence",
            "talking more than usual",
            "major depression episodes",
            "mood swings",
        ],
        "Hypomania lasts at least 4 days; depression lasts at least 2 weeks",
        ["bipolar 2", "hypomania", "depression with highs", "mood swings", "less severe mania"],
        "high",
    ),
    disorder(
        "Bipolar and Related Disorders",
        "Cyclothymic Disorder",
        "F34.0",
        "For at least 2 years, numerous periods of hypomanic symptoms and depressive symptoms have occurred without meeting full episode criteria.",
        "Symptoms are present for at least half the time, and the person has not been symptom-free for more than 2 months at a time.",
        "The pattern causes distress or impairment and is not better explained by bipolar disorder, substances, or medical illness.",
        [
            "chronic mood ups and downs",
            "periods of extra energy",
            "periods of low mood",
            "irritability",
            "unstable mood pattern",
        ],
        "At least 2 years",
        ["cyclothymia", "chronic mood swings", "mild bipolar pattern", "ups and downs", "unstable mood"],
        "medium",
    ),
    disorder(
        "Depressive Disorders",
        "Disruptive Mood Dysregulation Disorder",
        "F34.8",
        "Severe recurrent temper outbursts are grossly out of proportion to the situation and inconsistent with developmental level.",
        "Between outbursts, mood is persistently irritable or angry most of the day, nearly every day, in multiple settings.",
        "Symptoms last at least 12 months, begin before age 10, and are not better explained by bipolar disorder or another condition.",
        [
            "frequent severe temper outbursts",
            "chronic irritability",
            "anger between outbursts",
            "problems at home school or with peers",
        ],
        "At least 12 months",
        ["dmdd", "chronic irritability", "severe temper outbursts", "angry child", "frequent meltdowns"],
        "medium",
    ),
    disorder(
        "Depressive Disorders",
        "Major Depressive Disorder",
        "F33.1",
        "Five or more depressive symptoms are present during the same 2-week period, including depressed mood or loss of interest.",
        "Symptoms cause distress or impairment and may include sleep, appetite, energy, guilt, concentration, or suicidal changes.",
        "Episode is not due to substances or medical illness and is not better explained by bipolar disorder.",
        [
            "depressed mood",
            "loss of interest or pleasure",
            "sleep changes",
            "appetite or weight changes",
            "low energy",
            "feelings of worthlessness or guilt",
            "poor concentration",
            "suicidal thoughts",
        ],
        "At least 2 weeks",
        ["major depression", "depression", "sadness", "hopelessness", "loss of interest", "suicidal thoughts"],
        "high",
    ),
    disorder(
        "Depressive Disorders",
        "Persistent Depressive Disorder",
        "F34.1",
        "Depressed mood is present most of the day, more days than not, for a long period.",
        "During the depressed mood, at least two associated symptoms such as poor appetite, insomnia, low energy, low self-esteem, poor concentration, or hopelessness are present.",
        "Symptoms persist for the required duration without long symptom-free gaps and are not better explained by bipolar disorder or another condition.",
        [
            "chronic low mood",
            "low energy",
            "poor self-esteem",
            "hopelessness",
            "poor concentration",
            "sleep problems",
        ],
        "At least 2 years",
        ["dysthymia", "persistent depression", "chronic sadness", "long-term low mood", "hopelessness"],
        "medium",
    ),
    disorder(
        "Depressive Disorders",
        "Premenstrual Dysphoric Disorder",
        "N94.3",
        "In most menstrual cycles, mood symptoms appear in the final week before menses and improve shortly after onset of menses.",
        "Symptoms include marked mood swings, irritability, depressed mood, or anxiety plus additional physical or behavioral symptoms.",
        "Symptoms cause distress or impairment and are not simply an exacerbation of another disorder.",
        [
            "marked mood swings before periods",
            "irritability",
            "depressed mood",
            "anxiety or tension",
            "low energy",
            "changes in sleep or appetite",
        ],
        "Repeats across most menstrual cycles",
        ["pmdd", "severe pms", "period mood symptoms", "premenstrual depression", "premenstrual irritability"],
        "medium",
    ),
    disorder(
        "Anxiety Disorders",
        "Separation Anxiety Disorder",
        "F93.0",
        "Developmentally inappropriate fear or anxiety about separation from attachment figures is present.",
        "Symptoms may include distress when separated, worry about harm, refusal to go out alone, nightmares, or physical complaints.",
        "Fear lasts long enough to be clinically significant and is not better explained by another disorder.",
        [
            "extreme distress when separating",
            "worry that loved ones will be harmed",
            "refuses to be alone",
            "avoids school or leaving home",
            "nightmares about separation",
            "stomachaches or headaches during separation",
        ],
        "At least 4 weeks in children or 6 months in adults",
        ["separation anxiety", "fear of being away from parents", "clingy", "school refusal", "worry about loved ones"],
        "medium",
    ),
    disorder(
        "Anxiety Disorders",
        "Specific Phobia",
        "F40.298",
        "Marked fear or anxiety occurs about a specific object or situation.",
        "The feared object or situation almost always triggers immediate anxiety and is actively avoided or endured with intense fear.",
        "Fear is out of proportion, lasts at least 6 months, causes impairment, and is not better explained by another disorder.",
        [
            "intense fear of a specific trigger",
            "immediate anxiety response",
            "avoidance behavior",
            "panic when exposed to trigger",
            "fear feels excessive but hard to control",
        ],
        "At least 6 months",
        ["specific phobia", "intense fear", "avoidance", "fear of flying", "fear of needles", "fear of animals"],
        "medium",
    ),
    disorder(
        "Anxiety Disorders",
        "Social Anxiety Disorder",
        "F40.10",
        "Marked fear or anxiety about social situations involving possible scrutiny by others.",
        "The person fears acting in a way that will be negatively judged, and social situations are avoided or endured with intense anxiety.",
        "Fear is persistent, out of proportion, causes impairment, and is not better explained by another disorder or medical condition.",
        [
            "fear of embarrassment",
            "fear of being judged",
            "avoids social situations",
            "anxiety during conversations or performances",
            "blushing or shaking in social settings",
        ],
        "At least 6 months",
        ["social anxiety", "social phobia", "fear of judgment", "performance anxiety", "social avoidance"],
        "medium",
    ),
    disorder(
        "Anxiety Disorders",
        "Panic Disorder",
        "F41.0",
        "Recurrent unexpected panic attacks occur with sudden surges of intense fear and physical symptoms.",
        "At least one attack is followed by persistent worry about more attacks or maladaptive behavior change related to the attacks.",
        "Symptoms are not due to substances, medical illness, or another mental disorder.",
        [
            "sudden intense fear",
            "heart pounding",
            "shortness of breath",
            "dizziness",
            "chest discomfort",
            "fear of dying or losing control",
            "worry about future attacks",
        ],
        "At least 1 month of worry or behavior change after attacks",
        ["panic disorder", "panic attacks", "sudden fear", "chest tightness", "fear of another attack"],
        "medium",
    ),
    disorder(
        "Anxiety Disorders",
        "Agoraphobia",
        "F40.00",
        "Marked fear or anxiety occurs about situations where escape might be difficult or help may not be available if panic-like symptoms happen.",
        "Situations are actively avoided, require a companion, or are endured with intense fear.",
        "Fear is persistent, causes impairment, and is not better explained by another disorder.",
        [
            "fear of public transport",
            "fear of open spaces",
            "fear of enclosed spaces",
            "fear of crowds or lines",
            "fear of leaving home alone",
            "avoidance of places that feel hard to escape",
        ],
        "At least 6 months",
        ["agoraphobia", "fear of leaving home", "fear of crowds", "fear of being trapped", "avoidance of public places"],
        "medium",
    ),
    disorder(
        "Anxiety Disorders",
        "Generalized Anxiety Disorder",
        "F41.1",
        "Excessive anxiety and worry occur more days than not about multiple events or activities.",
        "The worry is hard to control and is associated with symptoms such as restlessness, fatigue, poor concentration, irritability, muscle tension, or sleep problems.",
        "Symptoms cause distress or impairment and are not due to substances, medical illness, or another mental disorder.",
        [
            "excessive worry",
            "difficulty controlling worry",
            "restlessness",
            "muscle tension",
            "irritability",
            "poor concentration",
            "sleep disturbance",
        ],
        "At least 6 months",
        ["gad", "generalized anxiety", "constant worry", "overthinking", "tense", "can't relax"],
        "medium",
    ),
    disorder(
        "Obsessive-Compulsive and Related Disorders",
        "Obsessive-Compulsive Disorder",
        "F42",
        "Obsessions, compulsions, or both are present.",
        "Obsessions are intrusive unwanted thoughts, and compulsions are repetitive behaviors or mental acts aimed at reducing distress or preventing feared outcomes.",
        "Symptoms are time-consuming or impairing and are not due to substances or another disorder.",
        [
            "intrusive unwanted thoughts",
            "excessive checking",
            "washing or cleaning rituals",
            "counting or repeating",
            "need for symmetry",
            "mental rituals",
        ],
        "Usually persistent; often more than 1 hour per day",
        ["ocd", "intrusive thoughts", "compulsions", "checking", "cleaning rituals", "obsessions"],
        "medium",
    ),
    disorder(
        "Obsessive-Compulsive and Related Disorders",
        "Body Dysmorphic Disorder",
        "F45.22",
        "There is a preoccupation with one or more perceived defects in appearance that are not observable or appear slight to others.",
        "The person performs repetitive behaviors or mental acts in response to appearance concerns.",
        "Preoccupation causes distress or impairment and is not better explained by an eating disorder.",
        [
            "constant concern about appearance flaws",
            "mirror checking",
            "excessive grooming",
            "seeking reassurance about looks",
            "comparing appearance with others",
            "avoiding social situations because of looks",
        ],
        "Persistent pattern",
        ["body dysmorphia", "appearance obsession", "feels ugly", "mirror checking", "fixated on flaw"],
        "medium",
    ),
    disorder(
        "Obsessive-Compulsive and Related Disorders",
        "Hoarding Disorder",
        "F42",
        "Persistent difficulty discarding possessions occurs regardless of actual value.",
        "The difficulty is driven by a perceived need to save items and distress linked to discarding them.",
        "Accumulation congests living areas or causes significant distress or impairment and is not better explained by another condition.",
        [
            "difficulty throwing things away",
            "strong urge to save items",
            "cluttered living spaces",
            "distress when discarding possessions",
            "excessive acquisition",
        ],
        "Persistent pattern",
        ["hoarding", "can't throw things away", "clutter", "saving everything", "distress discarding items"],
        "medium",
    ),
    disorder(
        "Obsessive-Compulsive and Related Disorders",
        "Trichotillomania",
        "F63.3",
        "Recurrent pulling out of one's hair leads to hair loss.",
        "The person repeatedly tries to stop or reduce the behavior.",
        "The behavior causes distress or impairment and is not better explained by another medical or mental condition.",
        [
            "recurrent hair pulling",
            "noticeable hair loss",
            "rising tension before pulling",
            "repeated attempts to stop",
        ],
        "Persistent or recurrent pattern",
        ["trichotillomania", "hair pulling", "pulling out hair", "body-focused repetitive behavior"],
        "medium",
    ),
    disorder(
        "Obsessive-Compulsive and Related Disorders",
        "Excoriation Disorder",
        "L98.1",
        "Recurrent skin picking leads to skin lesions.",
        "The person repeatedly tries to stop or reduce the picking.",
        "The behavior causes distress or impairment and is not better explained by another condition.",
        [
            "recurrent skin picking",
            "skin sores or lesions",
            "repeated attempts to stop",
            "picking during stress or boredom",
        ],
        "Persistent or recurrent pattern",
        ["skin picking", "excoriation", "picking at skin", "body-focused repetitive behavior"],
        "medium",
    ),
    disorder(
        "Trauma- and Stressor-Related Disorders",
        "Reactive Attachment Disorder",
        "F94.1",
        "A child shows a consistent pattern of emotionally withdrawn behavior toward adult caregivers.",
        "There is persistent social and emotional disturbance such as minimal comfort-seeking, limited positive affect, or unexplained irritability or fearfulness.",
        "The pattern follows severe neglect or insufficient caregiving, begins before age 5, and is not better explained by autism spectrum disorder.",
        [
            "rarely seeks comfort",
            "rarely responds to comfort",
            "social withdrawal",
            "limited positive emotion",
            "unexplained fearfulness",
            "history of neglect",
        ],
        "Begins before age 5 after severe neglect",
        ["reactive attachment", "attachment problems", "withdrawn child", "neglect history", "doesn't seek comfort"],
        "medium",
    ),
    disorder(
        "Trauma- and Stressor-Related Disorders",
        "Posttraumatic Stress Disorder",
        "F43.10",
        "Exposure to actual or threatened death, serious injury, or sexual violence is followed by intrusive trauma symptoms.",
        "There is persistent avoidance plus negative changes in mood or thinking and marked arousal or reactivity.",
        "Symptoms last more than 1 month, cause impairment, and are not due to substances or medical illness.",
        [
            "intrusive memories",
            "nightmares",
            "flashbacks",
            "avoidance of reminders",
            "emotional numbness",
            "hypervigilance",
            "startle response",
            "sleep problems",
        ],
        "More than 1 month",
        ["ptsd", "trauma", "flashbacks", "nightmares", "hypervigilance", "avoidance"],
        "high",
    ),
    disorder(
        "Trauma- and Stressor-Related Disorders",
        "Acute Stress Disorder",
        "F43.0",
        "After trauma exposure, the person develops intrusive, negative mood, dissociative, avoidance, or arousal symptoms.",
        "At least nine symptoms from these clusters are present.",
        "Symptoms begin or worsen after the trauma, last from 3 days to 1 month, and cause impairment.",
        [
            "intrusive memories",
            "distressing dreams",
            "feeling numb",
            "derealization",
            "avoidance of reminders",
            "sleep disturbance",
            "hypervigilance",
        ],
        "3 days to 1 month after trauma",
        ["acute stress disorder", "recent trauma", "flashbacks after trauma", "shock response", "trauma symptoms"],
        "high",
    ),
    disorder(
        "Trauma- and Stressor-Related Disorders",
        "Adjustment Disorder",
        "F43.20",
        "Emotional or behavioral symptoms develop in response to an identifiable stressor.",
        "Distress is out of proportion to the stressor and/or causes meaningful impairment in functioning.",
        "Symptoms begin within 3 months of the stressor, do not represent normal bereavement alone, and do not persist long after the stressor ends.",
        [
            "stress-related sadness",
            "stress-related anxiety",
            "trouble coping after a life change",
            "behavior changes after stress",
            "impaired work or school functioning",
        ],
        "Begins within 3 months of stressor; usually resolves within 6 months after stressor ends",
        ["adjustment disorder", "hard time coping", "stress reaction", "life change stress", "situational depression"],
        "medium",
    ),
    disorder(
        "Dissociative Disorders",
        "Dissociative Identity Disorder",
        "F44.81",
        "There is disruption of identity with two or more distinct personality states or an experience of possession.",
        "The disruption includes recurrent gaps in memory for everyday events, important information, or traumatic events.",
        "Symptoms cause distress or impairment and are not a normal cultural practice or due to substances or medical illness.",
        [
            "identity disruption",
            "distinct personality states",
            "memory gaps",
            "lost time",
            "feeling controlled by another state",
        ],
        "Persistent or recurrent pattern",
        ["did", "multiple identities", "lost time", "memory gaps", "identity switching"],
        "high",
    ),
    disorder(
        "Dissociative Disorders",
        "Dissociative Amnesia",
        "F44.0",
        "There is an inability to recall important autobiographical information, usually related to trauma or stress.",
        "The memory problem is too extensive to be ordinary forgetting.",
        "Symptoms cause distress or impairment and are not due to substances, neurological illness, or another disorder.",
        [
            "inability to recall personal information",
            "memory gaps after stress or trauma",
            "confusion about past events",
            "lost autobiographical memory",
        ],
        "Can be sudden or persistent",
        ["dissociative amnesia", "memory loss after trauma", "can't remember personal history", "trauma-related amnesia"],
        "medium",
    ),
    disorder(
        "Dissociative Disorders",
        "Depersonalization/Derealization Disorder",
        "F48.1",
        "Persistent or recurrent experiences of depersonalization, derealization, or both are present.",
        "Reality testing remains intact during the episodes.",
        "Symptoms cause distress or impairment and are not due to substances, medical illness, or another mental disorder.",
        [
            "feeling detached from self",
            "feeling unreal",
            "world feels dreamlike",
            "emotional numbing",
            "distorted sense of time",
        ],
        "Persistent or recurrent",
        ["depersonalization", "derealization", "feeling unreal", "detached from self", "dreamlike world"],
        "medium",
    ),
    disorder(
        "Somatic Symptom and Related Disorders",
        "Somatic Symptom Disorder",
        "F45.1",
        "One or more distressing physical symptoms are present.",
        "There are excessive thoughts, feelings, or behaviors related to the symptoms, such as persistent worry, high health anxiety, or excessive time and energy devoted to them.",
        "The symptomatic state is persistent even if a specific medical explanation is absent or changes.",
        [
            "distressing physical symptoms",
            "excessive worry about symptoms",
            "high health anxiety",
            "frequent medical visits",
            "a lot of time focused on bodily symptoms",
        ],
        "Typically more than 6 months",
        ["somatic symptom disorder", "physical symptoms and anxiety", "health worry", "symptom preoccupation", "body symptoms"],
        "medium",
    ),
    disorder(
        "Somatic Symptom and Related Disorders",
        "Illness Anxiety Disorder",
        "F45.21",
        "There is a preoccupation with having or getting a serious illness.",
        "Somatic symptoms are absent or mild, but anxiety about health is high, and the person easily becomes alarmed about bodily sensations.",
        "The illness fear is persistent, causes impairment, and is not better explained by another mental disorder.",
        [
            "fear of serious illness",
            "repeated body checking",
            "reassurance seeking",
            "avoiding doctors or repeatedly seeing doctors",
            "high health anxiety",
        ],
        "At least 6 months",
        ["illness anxiety", "health anxiety", "hypochondria", "fear of illness", "medical reassurance seeking"],
        "medium",
    ),
    disorder(
        "Somatic Symptom and Related Disorders",
        "Conversion Disorder",
        "F44.7",
        "One or more symptoms of altered voluntary motor or sensory function are present.",
        "Clinical findings show incompatibility between the symptom and recognized neurological or medical conditions.",
        "Symptoms cause distress or impairment or warrant medical evaluation and are not better explained by another disorder.",
        [
            "weakness or paralysis",
            "nonepileptic seizures",
            "abnormal movement",
            "speech symptoms",
            "sensory loss",
            "swallowing difficulty without clear neurological cause",
        ],
        "Acute episode or persistent pattern",
        ["conversion disorder", "functional neurological symptoms", "stress-related neurological symptoms", "nonepileptic seizures"],
        "medium",
    ),
    disorder(
        "Feeding and Eating Disorders",
        "Avoidant/Restrictive Food Intake Disorder",
        "F50.8",
        "An eating disturbance leads to persistent failure to meet nutritional or energy needs.",
        "The disturbance causes weight loss, nutritional deficiency, dependence on supplements or tube feeding, or marked interference with psychosocial functioning.",
        "It is not driven by body-image concerns and is not better explained by lack of food, a medical condition, or another mental disorder alone.",
        [
            "very limited food intake",
            "strong avoidance of certain foods",
            "weight loss or poor growth",
            "nutritional deficiency",
            "reliance on supplements",
            "fear of eating because of texture or choking",
        ],
        "Persistent pattern",
        ["arfid", "restrictive eating", "selective eating", "food avoidance", "poor nutrition without body image concerns"],
        "medium",
    ),
    disorder(
        "Feeding and Eating Disorders",
        "Anorexia Nervosa",
        "F50.01",
        "Restriction of energy intake leads to significantly low body weight.",
        "There is intense fear of gaining weight or persistent behavior that interferes with weight gain.",
        "Self-evaluation is overly influenced by body weight or shape, or the seriousness of low weight is not recognized.",
        [
            "restricted eating",
            "significantly low weight",
            "intense fear of weight gain",
            "distorted body image",
            "excessive exercise",
            "denial of seriousness of low weight",
        ],
        "Persistent pattern",
        ["anorexia", "starving self", "fear of weight gain", "very low weight", "body image distortion"],
        "high",
    ),
    disorder(
        "Feeding and Eating Disorders",
        "Bulimia Nervosa",
        "F50.2",
        "Recurrent binge eating occurs with a sense of loss of control.",
        "Recurrent compensatory behaviors are used to prevent weight gain, such as vomiting, laxatives, fasting, or excessive exercise.",
        "The binge-compensatory pattern occurs regularly, self-worth is overly tied to body shape or weight, and it does not occur only during anorexia nervosa.",
        [
            "binge eating",
            "loss of control while eating",
            "self-induced vomiting",
            "laxative misuse",
            "fasting after binges",
            "body image overconcern",
        ],
        "At least once a week for 3 months",
        ["bulimia", "binge and purge", "vomiting after eating", "loss of control eating", "compensatory behaviors"],
        "high",
    ),
    disorder(
        "Feeding and Eating Disorders",
        "Binge-Eating Disorder",
        "F50.8",
        "Recurrent binge eating episodes occur with a sense of loss of control.",
        "Binges are associated with features such as eating very rapidly, eating when not hungry, eating until uncomfortably full, eating alone because of embarrassment, or feeling guilty afterward.",
        "Episodes cause marked distress, occur regularly, and are not accompanied by recurrent compensatory behaviors.",
        [
            "eating unusually large amounts",
            "loss of control while eating",
            "eating rapidly",
            "eating when not hungry",
            "eating alone from embarrassment",
            "guilt after overeating",
        ],
        "At least once a week for 3 months",
        ["binge eating", "overeating", "loss of control eating", "emotional eating", "guilt after eating"],
        "medium",
    ),
    disorder(
        "Substance-Related and Addictive Disorders",
        "Alcohol Use Disorder",
        "F10.20",
        "A problematic pattern of alcohol use leads to impairment or distress, shown by multiple control, social, risky-use, or physical dependence symptoms.",
        "The person may drink more than intended, fail to cut down, spend a lot of time using alcohol, crave it, or keep drinking despite harm.",
        "Severity depends on the number of symptoms present within a 12-month period.",
        [
            "drinks more than intended",
            "can't cut down",
            "craving alcohol",
            "continues despite relationship or work problems",
            "tolerance",
            "withdrawal symptoms",
            "risky drinking",
        ],
        "Symptoms cluster within a 12-month period",
        ["alcohol use disorder", "alcohol dependence", "drinking problem", "can't stop drinking", "alcohol craving"],
        "high",
    ),
    disorder(
        "Substance-Related and Addictive Disorders",
        "Cannabis Use Disorder",
        "F12.20",
        "A problematic pattern of cannabis use leads to impairment or distress with multiple substance-use symptoms.",
        "The person may use more than intended, fail to cut down, crave cannabis, or continue despite social, work, or health problems.",
        "Severity depends on the number of symptoms within a 12-month period.",
        [
            "uses cannabis more than intended",
            "can't cut down",
            "craving cannabis",
            "keeps using despite problems",
            "tolerance",
            "withdrawal-like irritability or sleep issues",
        ],
        "Symptoms cluster within a 12-month period",
        ["cannabis use disorder", "marijuana dependence", "weed problem", "can't stop using cannabis", "cannabis craving"],
        "medium",
    ),
    disorder(
        "Substance-Related and Addictive Disorders",
        "Opioid Use Disorder",
        "F11.20",
        "A problematic pattern of opioid use leads to impairment or distress with multiple substance-use symptoms.",
        "The person may use more than intended, fail to cut down, crave opioids, or continue despite harm, and may develop tolerance or withdrawal.",
        "Severity depends on symptom count within a 12-month period.",
        [
            "opioid craving",
            "uses more than intended",
            "can't cut down",
            "continues despite harm",
            "tolerance",
            "withdrawal symptoms",
            "risky use",
        ],
        "Symptoms cluster within a 12-month period",
        ["opioid use disorder", "opioid dependence", "pain pill addiction", "heroin addiction", "withdrawal", "overdose risk"],
        "high",
    ),
    disorder(
        "Substance-Related and Addictive Disorders",
        "Stimulant Use Disorder",
        "F15.20",
        "A problematic pattern of stimulant use leads to impairment or distress with multiple substance-use symptoms.",
        "The person may use more than intended, fail to cut down, crave stimulants, or continue despite social, occupational, or medical harm.",
        "Severity depends on symptom count within a 12-month period.",
        [
            "stimulant craving",
            "uses more than intended",
            "can't cut down",
            "continues despite consequences",
            "tolerance",
            "withdrawal with fatigue or low mood",
            "risky behavior during use",
        ],
        "Symptoms cluster within a 12-month period",
        ["stimulant use disorder", "cocaine addiction", "amphetamine addiction", "stimulant dependence", "crash after stimulant use"],
        "high",
    ),
    disorder(
        "Substance-Related and Addictive Disorders",
        "Tobacco Use Disorder",
        "F17.200",
        "A problematic pattern of tobacco use leads to impairment or distress with multiple dependence symptoms.",
        "The person may use more than intended, fail to quit, crave nicotine, or continue despite health problems.",
        "Severity depends on symptom count within a 12-month period.",
        [
            "strong nicotine craving",
            "repeated failed quit attempts",
            "uses despite health risks",
            "withdrawal irritability",
            "tolerance",
            "uses soon after waking",
        ],
        "Symptoms cluster within a 12-month period",
        ["tobacco use disorder", "nicotine dependence", "smoking addiction", "can't quit smoking", "nicotine craving"],
        "medium",
    ),
    disorder(
        "Disruptive, Impulse-Control, and Conduct Disorders",
        "Oppositional Defiant Disorder",
        "F91.3",
        "A pattern of angry or irritable mood, argumentative or defiant behavior, or vindictiveness is present.",
        "Symptoms occur during interaction with at least one person who is not a sibling and cause impairment.",
        "The pattern is not better explained by psychotic, substance, depressive, or bipolar disorders.",
        [
            "often loses temper",
            "argues with authority figures",
            "defies rules",
            "blames others",
            "easily annoyed",
            "spiteful or vindictive behavior",
        ],
        "At least 6 months",
        ["odd", "oppositional behavior", "defiant child", "argues with adults", "irritable and angry"],
        "medium",
    ),
    disorder(
        "Personality Disorders",
        "Antisocial Personality Disorder",
        "F60.2",
        "There is a pervasive pattern of disregard for and violation of the rights of others since age 15.",
        "The pattern includes behaviors such as deceitfulness, impulsivity, aggression, irresponsibility, or lack of remorse, and the person is at least age 18 with evidence of conduct disorder before age 15.",
        "Behavior is not exclusively during schizophrenia or bipolar disorder.",
        [
            "lying or manipulation",
            "rule breaking",
            "aggression",
            "reckless disregard for safety",
            "irresponsibility",
            "lack of remorse",
        ],
        "Stable pattern since adolescence or early adulthood",
        ["antisocial personality", "sociopathic traits", "chronic rule breaking", "lack of remorse", "manipulative behavior"],
        "high",
    ),
    disorder(
        "Personality Disorders",
        "Borderline Personality Disorder",
        "F60.3",
        "A pervasive pattern of instability in relationships, self-image, and emotions with marked impulsivity is present.",
        "The pattern includes symptoms such as frantic efforts to avoid abandonment, unstable relationships, identity disturbance, impulsivity, self-harm, affective instability, emptiness, anger, or transient paranoia/dissociation.",
        "The pattern is stable across time and situations and begins by early adulthood.",
        [
            "fear of abandonment",
            "unstable intense relationships",
            "identity disturbance",
            "impulsivity",
            "self-harm or suicidal behavior",
            "rapid mood shifts",
            "chronic emptiness",
            "intense anger",
        ],
        "Long-standing pattern beginning by early adulthood",
        ["borderline personality", "bpd", "fear of abandonment", "self-harm", "unstable relationships", "emotional swings"],
        "high",
    ),
]


def validate_pdf_anchors(disorders):
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"DSM source PDF not found: {PDF_PATH}")

    reader = PdfReader(str(PDF_PATH))
    names_left = {item["name"] for item in disorders}
    for page in reader.pages:
        text = (page.extract_text() or "").lower()
        for name in list(names_left):
            if name.lower() in text:
                names_left.remove(name)
        if not names_left:
            break

    if names_left:
        raise ValueError(f"Could not anchor these disorders in the PDF text: {sorted(names_left)}")


def validate_json(disorders):
    if len(disorders) != 50:
        raise ValueError(f"Expected 50 disorders, found {len(disorders)}")

    required_keys = {"category", "name", "code", "criteria", "symptoms", "duration", "severity", "keywords", "risk_level"}
    seen_names = set()
    valid_risk = {"low", "medium", "high"}

    for item in disorders:
        if set(item.keys()) != required_keys:
            raise ValueError(f"Invalid keys for {item.get('name')}: {sorted(item.keys())}")
        if not item["name"] or item["name"] in seen_names:
            raise ValueError(f"Duplicate or empty disorder name: {item['name']}")
        seen_names.add(item["name"])

        if set(item["criteria"].keys()) != {"A", "B", "C"}:
            raise ValueError(f"Criteria keys invalid for {item['name']}")

        if item["severity"] != ["mild", "moderate", "severe"]:
            raise ValueError(f"Severity invalid for {item['name']}")

        if item["risk_level"] not in valid_risk:
            raise ValueError(f"Invalid risk level for {item['name']}: {item['risk_level']}")

        symptom_ids = set()
        symptom_texts = set()
        for symptom in item["symptoms"]:
            if set(symptom.keys()) != {"id", "text"}:
                raise ValueError(f"Invalid symptom schema for {item['name']}")
            if not re.fullmatch(r"[a-z0-9_]+", symptom["id"]):
                raise ValueError(f"Non-snake_case symptom id in {item['name']}: {symptom['id']}")
            if symptom["id"] in symptom_ids:
                raise ValueError(f"Duplicate symptom id in {item['name']}: {symptom['id']}")
            norm_text = symptom["text"].strip().lower()
            if norm_text in symptom_texts:
                raise ValueError(f"Duplicate symptom text in {item['name']}: {symptom['text']}")
            symptom_ids.add(symptom["id"])
            symptom_texts.add(norm_text)


def main():
    validate_pdf_anchors(DATA)
    validate_json(DATA)
    OUTPUT_PATH.write_text(json.dumps(DATA, indent=2, ensure_ascii=True), encoding="utf-8")
    print(f"Wrote {len(DATA)} disorders to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
