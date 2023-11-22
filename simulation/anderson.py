from poincare import System, initial, Variable, Parameter, assign

class Anderson(System):

    n1: Variable = initial(default=0)
    n2: Variable = initial(default=0)
    n3: Variable = initial(default=0)
    n4: Variable = initial(default=0)
    n5: Variable = initial(default=0)
    n6: Variable = initial(default=0)
    n7: Variable = initial(default=0)
    n8: Variable = initial(default=0)
    n9: Variable = initial(default=0)

    n1yb: Variable = initial(default=0)
    n2yb: Variable = initial(default=0)

    kNR3: Parameter = assign(default=0)
    kNR2: Parameter = assign(default=0)
    kNR4: Parameter = assign(default=0)
    kNR5: Parameter = assign(default=0)
    kNR6: Parameter = assign(default=0)
    kNR7: Parameter = assign(default=0)
    kNR8: Parameter = assign(default=0)
    kNR9: Parameter = assign(default=0)

    kET1_3: Parameter = assign(default=0)
    kET2_5: Parameter = assign(default=0)
    kET3_1: Parameter = assign(default=0)
    kET3_7: Parameter = assign(default=0)
    kET5_8: Parameter = assign(default=0)
    kET6_9: Parameter = assign(default=0)
    kET7_3: Parameter = assign(default=0)
    kET9_5: Parameter = assign(default=0)

    kR2: Parameter = assign(default=0)
    kR3: Parameter = assign(default=0)
    kR5: Parameter = assign(default=0)
    kR6: Parameter = assign(default=0)
    kR8: Parameter = assign(default=0)

    kCR4: Parameter = assign(default=0)
    kCR6: Parameter = assign(default=0)
    kCR9: Parameter = assign(default=0)

    kUC2: Parameter = assign(default=0)
    kUC5: Parameter = assign(default=0)

    kYb: Parameter = assign(default=0)

    F: Parameter = assign(default=0)
    sigma_yb: Parameter = assign(default=0)
    sigma_er: Parameter = assign(default=0)


    n9.derive() << kET6_9 * n6 * n2yb - kET9_5 * n9 * n1yb - kNR9 * n9 - kCR9 * n9 * n1

    n8.derive() << kET5_8 * n5 * n2yb + kNR9 * n9 - kNR8 * n8 - kR8 * n8

    n7.derive() << kNR8 * n8 + kET3_7 * n3 * n2yb - kET7_3 * n7 * n1yb - kNR7 * n7 + kUC5 * n3 * n5 + kCR9 n9 * n1

    n6.derive() << kNR7 * n7 - kET6_9 * n6 * n2yb - kNR6 * n6 - kR6 * n6 - kCR6 * n6 *n1

    n5.derive() << kNR6 * n6 + kET2_5 * n2 * n2yb + 0.04 * kR8 * n8 - kET5_8 * n5 * n2yb + kET9_5 * n9 * n1yb - (kNR5 + kR5) * n5 - kUC5 * n3 * n5

    n4.derive() << kNR5 * n5 + kUC2 * n2 * n2 - kCR4 * n4 * n1 - kNR4 * n4

    n3.derive() << F*sigma_er * n1 + kNR4 * n4 + kET1_3 * n1 * n2yb + kET7_3 * n7 * n1yb + kCR6 * n6 * n1 + 0.05 * kR5 * n5 + 0.05 * kR6 * n6 + 0.14 * kR8 * n8 - kET3_1 * n3 * n1yb - kET3_7 * n3 * n2yb - (kNR3 + kR3) * n3 - kUC5 * n3 * n5

    n2.derive() << kNR3 * n3 + 0.19 * kR3 * n3 + 0.05 * kR5 * n5 + 0.25 * kR6 * n6 + 0.42 * kR8 * n8 + kCR6 * n6 * n1 + 2 * kCR4 * n4 * n1 - 2 * kUC2 * n2 * n2 - (kR2 + kNR2) * n2 - kUC5 * n3 * n5 + kCR9 * n9 * n1

    n1.derive() << -F * sigma_er * n1 + kNR2 * n2 + 0.81 * kR3 * n3 + 0.90 * kR5 * n5 + 0.70 * kR6 * n6 + 0.40 * kR8 * n8 - kCR6 * n6 * n1 - kCR4 *n4 * n1 + kUC2 * n2 * n2 - kET1_3 * n1 * n2yb + kET3_1 * n3 * n1yb - kCR9 * n9 * n1

    n1yb.derive() << -n2yb.derive()
    
    n2yb.derive() << F * sigma_yb * n1yb - kYb * n2yb - kET1_3 * n1 * n2yb - kET2_5 * n2 * n2yb - kET3_7 * n3 * n2yb - kET5_8 * n5 * n2yb - kET6_9 * n6 * n2yb + kET3_1 * n3 * n1yb + kET7_3 * n7 * n1yb + kET9_5 * n9 * n1yb


